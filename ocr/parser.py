'''
Parser.py

'''

import sys
import os
import io
from . import ocrscan
from . import pdfpage
from . import word
import bisect
from sortedcontainers import SortedDict
import templates.template


class Parser():

    def pdf_contains_word(word, pdf):
        return (word in pdf.text_dict)

    def text_contains_word(word, text):
        if word in text:
            return True
        else:
            return False

    # given an x and y coordinate, checks to see if
    # a word is at that coordinate in the pdf,
    # within a certain tolerance value of pixels
    def is_word_at_location(word, x, y, pdf, tolerance=10):
        # we can check within a certain pixel area by adding a tolerance of how many pixels the x and y can deviate
        # from the designated location

        # in case there are no words, return false
        if (len(pdf.position_dict) == 0):
            return False

        # otherwise, there is always at least one value

        # the position dictionary is a Sorted Dictionary of Sorted Dictionaries
        # first, bisect the Sorted dictionary to get the index of closest value
        x_index = (pdf.position_dict).bisect(x)

        # bisect bisects right, so if you're choosing a value higher than the highest x value,
        # it will retun an out-of-bounds index. Thus, you need to decrement the array in this
        # situation
        if (x_index == len(pdf.position_dict)):
            x_index -= 1

        # get the dictionary key using the index - this is also the
        # x-coordinate
        x_key = pdf.position_dict.iloc[x_index]
        print(x_key)

        # if the x coordinate of the word is less than [tolerance] pixels away,
        # check the y coordinate
        if (x_key < x + tolerance) and (x_key > x - tolerance):
            if Parser.is_word_at_location_y(word, x_key, y, pdf, tolerance):
                return True

        # if the x-coordinate doesn't match, check all values above and below
        # within the tolerance range

        # increase/decrease the indices
        x_index_plus = x_index + 1
        x_index_minus = x_index - 1

        # an initial check to see if we are allowed to pull a key from this
        # index without going out of range
        if (x_index_plus < len(pdf.position_dict)):
            x_key = (pdf.position_dict).iloc[x_index_plus]

        # check up to [tolerance] pixels greater than the x-coordinate
        # while the x coordinate has not reached the tolerance limit, and while
        # the index is not out of range
        while ((x_key < x + tolerance)
               and (x_index_plus < len(pdf.position_dict))):
            x_key = pdf.position_dict.iloc[x_index_plus]
            # check if the new key has a y-coordinate that works
            if Parser.is_word_at_location_y(word, x_key, y, pdf, tolerance):
                return True

            # if not, increment the index and try again
            x_index_plus += 1

        # check up to [tolerance] pixels less than the x-coordinate
        # while the x coordinate has not reached the tolerance limit, and while
        # the index is not out of range
        if (x_index_minus >= 0):
            x_key = (pdf.position_dict).iloc[x_index_minus]

        while ((x_key > x - tolerance) and (x_index_minus >= 0)):
            x_key = pdf.position_dict.iloc[x_index_minus]
            # check if the new key has a y-coordinate that works
            if Parser.is_word_at_location_y(word, x_key, y, pdf, tolerance):
                return True

            # if not, increment the index and try again
            x_index_minus -= 1

        # if we have check the entire range of possible x-coordinates and none of them work,
        # word is not at location
        return False

    # the second half of the "is_word_at location function"
    # given a possible x-coordinate, checks to see if there is a y-coordinate
    # that fits
    def is_word_at_location_y(word, x_key, y, pdf, tolerance):

        # the position dictionary is a Sorted Dictionary of Sorted Dictionaries
        # first, bisect the Sorted dictionary to get the index of closest value
        y_index = (pdf.position_dict[x_key]).bisect(y)

        # bisect bisects right, so if you're choosing a value higher than the highest x value,
        # it will retun an out-of-bounds index. Thus, you need to decrement the array in this
        # situation
        if (y_index == len(pdf.position_dict[x_key])):
            y_index -= 1

        # get the dictionary key using the index - this is also the
        # y-coordinate
        y_key = pdf.position_dict[x_key].iloc[y_index]

        # if the x coordinate of the word is less than [tolerance] pixels away
        if (y_key < y + tolerance) and (y_key > y - tolerance):
            # return true if word in text
            if word in (pdf.position_dict[x_key])[y_key].get_text():
                return True

        # increment/decrement the indices
        y_index_plus = y_index + 1
        y_index_minus = y_index - 1

        # an initial check to see if we are allowed to pull a key from this
        # index without going out of range
        if (y_index_plus < len(pdf.position_dict[x_key])):
            y_key = (pdf.position_dict[x_key]).iloc[y_index_plus]

        # check up to [tolerance] pixels greater than the y-coordinate
        # while the y coordinate has not reached the tolerance limit, and while
        # the index is not out of range
        while ((y_key < y + tolerance)
               and (y_index_plus < len(pdf.position_dict[x_key]))):
            y_key = (pdf.position_dict[x_key]).iloc[y_index_plus]
            # return true if word in text
            if word in pdf.position_dict[x_key][y_key].get_text():
                return True

            # otherwise, increment the index and try again
            y_index_plus += 1
            y_key = (pdf.position_dict[x_key]).iloc[y_index_plus]

        # an initial check to see if we are allowed to pull a key from this
        # index without going out of range
        if (y_index_minus >= 0):
            y_key = (pdf.position_dict[x_key]).iloc[y_index_minus]

        # check up to [tolerance] pixels less than the y-coordinate
        # while the y coordinate has not reached the tolerance limit, and while
        # the index is not out of range
        while ((y_key > y - tolerance) and (y_index_minus >= 0)):
            y_key = (pdf.position_dict[x_key]).iloc[y_index_minus]
            # return true if word is in text
            if word in pdf.position_dict[x_key][y_key].get_text():
                return True

            # otherwise, decrement and try again
            y_index_minus -= 1
            y_key = (pdf.position_dict[x_key]).iloc[y_index_minus]

        # if we have check the entire range of possible x-coordinates and none of them work,
        # word is not at this x location
        return False

    def identify_document(pdf, template_folder):
        # for each template
        # load a template (right now, just a sample template is being created)
        # possible improvement: hashing with a max keyword size

        # open the templates folder
        for file in os.listdir(template_folder):
            if file.endswith('.template'):

                template_to_check = template.load_from_file(
                    "{}/{}".format(template_folder, file))
                print("Checking template {}".format(template_to_check.get_name()))

                # for each keyword
                for i in range(0, template_to_check.keyword_list_length("id")):

                    keyword = template_to_check.keyword_at_index("id", i)
                    keyword_text = (
                        template_to_check.keyword_at_index(
                            "id", i)).get_text()
                    print("Checking keyword {}".format(keyword_text))
                    # check if it is in the text dictionary - this assumes correct
                    # words!
                    for key in pdf.text_dict.keys():
                        if keyword_text in key:
                            # note its deviation from its x-y location
                            for j in range(0, len(pdf.text_dict[key])):
                                x_deviation = (
                                    keyword.get_x() - pdf.text_dict[key][j].get_x())
                                y_deviation = (
                                    keyword.get_y() - pdf.text_dict[key][j].get_y())

                                # check if all the other keywords are where they're supposed to be, given the deviation
                                # all must match
                                keyword_match = True
                                for i in range(
                                        0, template_to_check.keyword_list_length("id")):
                                    keyword = template_to_check.keyword_at_index(
                                        "id", i)
                                    # print(keyword.get_text())
                                    keyword_text = (
                                        template_to_check.keyword_at_index(
                                            "id", i)).get_text()
                                    if (Parser.is_word_at_location(keyword_text, keyword.get_x(
                                    ) - x_deviation, keyword.get_y() - y_deviation, pdf, tolerance=10) == False):
                                        keyword_match = False

                                if (keyword_match):
                                    return template_to_check

        return None
