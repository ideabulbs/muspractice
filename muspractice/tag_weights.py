#!/usr/bin/env python
import subprocess
import os
import re
import json
import operator

CONFIG_FILENAME = '.muspractice_tag_weights'
LOCAL_CONFIG_FILENAME = '%s/%s' % (os.getcwd(), CONFIG_FILENAME)
GLOBAL_CONFIG_FILENAME = '%s/%s' % (os.environ['HOME'], CONFIG_FILENAME)

def get_config_path():
    """
    Find appropriate config file with target tag weights. Local file
    in the current directory will override the global file in home
    directory.

    Filenames:
    - .muspractice_tag_weights (current working directory)
    - ~/.muspractice_tag_weights (global)
    """
    if os.path.exists(LOCAL_CONFIG_FILENAME):
        return LOCAL_CONFIG_FILENAME
    elif os.path.exists(GLOBAL_CONFIG_FILENAME):
        return GLOBAL_CONFIG_FILENAME
    return None

def get_config():
    """Read target weights from config file"""
    config_file = get_config_path()
    if not config_file:
        raise RuntimeError('Could not find tag weight config: either %s or %s' % (LOCAL_CONFIG_FILENAME, GLOBAL_CONFIG_FILENAME))
    with open(config_file, 'r') as inp:
        config_dict = json.load(inp)
    return config_dict

CONFIG = get_config()

def get_data():
    """Read repetition data from muspractice"""
    cmd = "python muspractice -R | tail -n %s" % CONFIG['history_length']
    popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    result = []
    for line in stdout.splitlines():
        tagline = line.split(':::')[-2]
        tagline = re.sub(' +', ' ', tagline)
        tags = tagline.split(' ')
        result.append(tags)
    return result

def get_unique_tags(phrase_tag_list):
    """Create a list of unique tags"""
    unique_tags = []
    for item in phrase_tag_list:
        for tag in item:
            if tag not in unique_tags:
                unique_tags.append(tag)
    return unique_tags

def get_tag_weights(phrase_tag_list):
    """Calculate current tag weights in the repetition data"""
    unique_tags = get_unique_tags(phrase_tag_list)
    total_repetition_count = len(phrase_tag_list)
    result = dict()
    for tag in unique_tags:
        for item in phrase_tag_list:
            if tag in item:
                if tag not in result.keys():
                    result[tag] = 0
                result[tag] += 1
    for tag, reps in result.iteritems():
        result[tag] = reps / float(total_repetition_count)
    return result

def print_weights(sorted_diff, limit=None):
    """Print the calculated weights"""
    out = ""
    list_range = sorted_diff
    if limit is not None:
        list_range = sorted_diff[:limit]

    for item in list_range:
        out += "%s:%.2f " % (item[0], item[1])
    print out

def main():
    """main"""
    data = get_data()
    current_weights = get_tag_weights(data)
    target_weights = CONFIG['tag_weights']
    
    diff_dict = dict()
    for tag, value in target_weights.iteritems():
        if tag in current_weights.keys():
            diff_dict[tag] = target_weights[tag] - current_weights[tag]
        else:
            diff_dict[tag] = target_weights[tag]

    sorted_diff = sorted(diff_dict.items(), key=operator.itemgetter(1))
    sorted_diff.reverse()
    
    if len(sorted_diff) > 3:
        limit = 3
    else:
        limit = None
    print_weights(sorted_diff, limit=limit)


if __name__ == '__main__':
    main()
