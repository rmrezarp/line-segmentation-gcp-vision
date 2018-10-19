#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: rmreza

Module to fixing the bounding box from googlevisionapi OCR
so we can get text per lines

as seen on :
https://github.com/sshniro/line-segmentation-algorithm-to-gcp-vision/
converted into Python and doing some modification due to some error produced

issues :
The algorithm succesfully works for most of the slanted and slightly crumpled
images. But it will fail to highly crumpled or folded images.
"""

import json
import os
from copy import deepcopy

from . import coordinatesHelper as ch


def mergeNearByWords(data):
    """
    function to merge words that closes into a one bounding box
    parsing json data from googlevisionapi
    return finalArray as text object
    """

    if not data or not data.get("textAnnotations", None):
        return None

    yMax = ch.getYMax(data)
    data = ch.invertAxis(data, yMax)
    # Auto identified and merged lines from gcp vision

    lines = data["textAnnotations"][0]["description"].split('\n')
    print(lines)

    # gcp vision full text
    rawText = deepcopy(data["textAnnotations"])

    # reverse to use lifo, because array.shift() will consume 0(n)
    lines.reverse()
    rawText.reverse()

    # to remove the zeroth element which gives the total summary of the text
    rawText.pop()
    mergedArray = getMergedLines(lines, rawText)


# old
    # ch.getBoundingPolygon(mergedArray)

    # #sort by y maximum then sort by x minimum
    # ch.minmax(mergedArray)
    # mergedArray = sorted(mergedArray,
    # key=lambda x: (
    # x['boundingPoly']['minmax'][0],
    # -x['boundingPoly']['minmax'][1]))
    # ch.combineBoundingPolygon(mergedArray)

# new
    ch.minmax(mergedArray)
    mergedArray = sorted(mergedArray, key=lambda x: (
        x['boundingPoly']['minmax'][0], -x['boundingPoly']['minmax'][1]))

    ch.getBoundingPolygon(mergedArray)

    # sort by y maximum then sort by x minimum
    ch.combineBoundingPolygon(mergedArray)

    mergedArray = ch.traverseBoundingPolygon(mergedArray)

# for item in mergedArray:
#     print(item)
#     #if item["matched"] or len(item['match']) > 0:
#     if len(item['match']) > 0:
#         print(item)
# mergedArray = deepcopy(a)

# for item in mergedArray:
#     print(item)
#     print("{} x,y = ({},{})".format(item['description'],
# item['boundingPoly']['minmax'][0],item['boundingPoly']['minmax'][1]))

# print("mergedArray")

    # This does the line segmentation based on the bounding boxes
    # return mergedArray

    finalArray = constructLineWithBoundingPolygon(mergedArray)
    return finalArray

# TO DO implement the line ordering for multiple words


def constructLineWithBoundingPolygon(mergedArray):
    """
    function to imaginary make and connect some polygon object that overlapping
    by doing line segmentation so it becomes a one bounding box
    parsing mergedArray an array of four points that build a bounding polygon
    return result as a text object
    """
    finalArray = []
    for i, item in enumerate(mergedArray):
        # print("\n")
        # print(i, ' =', item["description"])
        # print(item)
        # print(item["match"])
        # print(item["matched"])
        # print(i, ' =' , item["boundingPoly"]["vertices"])
        if not item["matched"]:
            # print("have child")
            if len(item["match"]) == 0:
                # print("no match")
                yMax = max([vertex['y']
                            for vertex in item["boundingPoly"]["vertices"]])
                # print("no have match {}".format(item['description']))
                finalArray.append([item["description"], yMax])
            else:
                # print("best match")
                # print(item['description'])
                # arrangeWordsInOrder(mergedArray, i)
                # index = item['match'][0]['matchLineNum']
                # print(index)
                # secondPart = mergedArray[index]["description"]
                # print(secondPart)
                # print(item["description"] + ' ' + secondPart)
                # yMax = max(
                # [vertex['y'] for vertex in item["boundingPoly"]["vertices"]])
                # print(yMax)
                # finalArray.append(
                # [item["description"] + ' ' + secondPart,yMax])

                # print("best match {}".format(item['description']))
                finalArray.append(arrangeWordsInOrder(mergedArray, i))
        else:
            # print("matched with something {}".format(item['description']))
            # print()

            # print("dont have child")
            continue
    # print("\n")
    # print("=" * 10)
    finalArray = sorted(finalArray, key=lambda x: x[1], reverse=True)
    # return finalArray

    print("="*10)
    # print(finalArray)
    result = [item[0] for item in finalArray]
    result = "\n".join(result)
    return result


def getMergedLines(lines, rawText):
    """
    function to merge the overlapping points
    - parsing lines as a googlevisionapi OCR full result per lines
    - parsing rawText as a googlevisionapi OCR full result per lines
      basically a copy of lines, used to comparing
    return mergedArray as a list object
    """
    mergedArray = []
    while len(lines) != 1:
        l = lines.pop()
        l1 = deepcopy(l)
        status = True

        data = ""
        mergedElement = ""

        while True:
            try:
                wElement = rawText.pop()
            except:
                break

            w = wElement["description"]
            elVer = wElement["boundingPoly"]["vertices"]
            try:
                index = str(l).index(str(w))
            except:
                if status:
                    status = False
                    # set starting coordinates
                    mergedElement = wElement

                print("failed on this character = {}".format(str(w)))

                mergedElement["description"] = l1
                mergedElement["boundingPoly"]["vertices"][1] = elVer[1]
                mergedElement["boundingPoly"]["vertices"][2] = elVer[2]
                mergedArray.append(mergedElement)
                break
            # check if the word is inside
            l = l[index + len(w):]
            if status:
                status = False
                # set starting coordinates
                mergedElement = wElement

            if l == "":
                # set ending coordinates
                mergedElement["description"] = l1
                mergedElement["boundingPoly"]["vertices"][1] = elVer[1]
                mergedElement["boundingPoly"]["vertices"][2] = elVer[2]
                mergedArray.append(mergedElement)
                break

    return mergedArray


def arrangeWordsInOrder(mergedArray, k):
    """
    function to arrange the words per lines based on a points
    - parsing mergedArray as data
    - parsing k as an index array
    return mergedLine as the data per line and yMax as maximum point as a base
    """

    print("*****" * 10)
    matched = [mergedArray[k]]

    line = mergedArray[k]['match']
    temp = [mergedArray[item['matchLineNum']] for item in line]
    matched.extend(temp)
    matched = sorted(
        matched, key=lambda k: k["boundingPoly"]["vertices"][0]["x"])

    temp_mergedLine = []
    temp_max = 0
    for item in matched:
        temp_yMax = max([vertex['y']
                         for vertex in item["boundingPoly"]["vertices"]])
        # print("ymax ",temp_yMax)
        if temp_yMax >= temp_max:
            temp_max = temp_yMax
        temp_mergedLine.append(item["description"])

    mergedLine = " ".join(temp_mergedLine)
    yMax = temp_max
    #
    print(">>>>> ", mergedLine)
    print("+++++ ", yMax)
    print("----", [mergedLine, yMax])
    return [mergedLine, yMax]
