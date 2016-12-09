#!/usr/bin/python
import subprocess
import re
import json
import operator

def get_config():
    with open('.muspractice_tag_weights.json', 'r') as inp:
        config_dict = json.load(inp)
    return config_dict

CONFIG = get_config()

def get_data():
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
    unique_tags = []
    for item in phrase_tag_list:
        for tag in item:
            if tag not in unique_tags:
                unique_tags.append(tag)
    return unique_tags

def get_tag_weights(phrase_tag_list):
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
    out = ""
    list_range = sorted_diff
    if limit is not None:
        list_range = sorted_diff[:limit]

    for item in list_range:
        out += "%s:%.2f " % (item[0], item[1])
    print out

def main():
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
