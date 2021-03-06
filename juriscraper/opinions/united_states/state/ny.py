"""
Scraper for New York Court of Appeals
CourtID: ny
Court Short Name: NY
History:
 2014-07-04: Created by Andrei Chelaru, reviewed by mlr.
 2015-10-23: Parts rewritten by mlr.
 2016-05-04: Updated by arderyp to handle typos in docket string format
"""

import re
from lxml import html
from lxml.html import html5parser, fromstring, tostring
from datetime import date

from juriscraper.OpinionSite import OpinionSite
from juriscraper.lib.string_utils import convert_date_string


class Site(OpinionSite):
    DOWNLOAD_URL_SUB_PATH = "td[2]//@href[not(contains(., 'DecisionList'))]"
    FOUR_CELLS_SUB_PATH = '//*[count(td)=4'

    def __init__(self, *args, **kwargs):
        super(Site, self).__init__(*args, **kwargs)
        self.crawl_date = date.today()
        # https://www.nycourts.gov/ctapps/Decisions/2015/Dec15/Dec15.html
        self.url = 'http://www.nycourts.gov/ctapps/Decisions/{year}/{mon}{yr}/{mon}{yr}.html'.format(
            year=self.crawl_date.year,
            yr=self.crawl_date.strftime("%y"),
            mon=self.crawl_date.strftime("%b"))
        self.court_id = self.__module__

    def _make_html_tree(self, text):
        e = html5parser.document_fromstring(text)
        html_tree = fromstring(tostring(e))
        return html_tree

    def _get_case_names(self):
        path = '%s and %s]' % (
            self.FOUR_CELLS_SUB_PATH, self.DOWNLOAD_URL_SUB_PATH)
        case_names = []
        for element in self.html.xpath(path):
            case_name_parts = []
            for t in element.xpath('./td[4]/p/font/text()'):
                if t.strip():
                    case_name_parts.append(t)
            if not case_name_parts:
                # No hits for first XPath, try another that sometimes works.
                for t in element.xpath('./td[4]//text()'):
                    if t.strip():
                        case_name_parts.append(t)
            if case_name_parts:
                case_names.append(', '.join(case_name_parts))
        return case_names

    def _get_download_urls(self):
        return self.html.xpath('%s]/%s' % (
            self.FOUR_CELLS_SUB_PATH,
            self.DOWNLOAD_URL_SUB_PATH
        ))

    def _get_case_dates(self):
        case_dates = []
        for row in self.html.xpath('//tr[not(.//table)]'):
            # self.date gets set when below condition fails
            if not self._row_contains_date(row):
                if self._row_contains_opinion(row):
                    case_dates.append(self.date)
        return case_dates

    def _get_precedential_statuses(self):
        return ['Published'] * len(self.case_names)

    def _get_docket_numbers(self):
        docket_numbers = []
        for cell in self.html.xpath('%s]/td[1]' % self.FOUR_CELLS_SUB_PATH):
            text_node_strings = ', '.join(cell.xpath('.//text()'))
            if re.search(r'No\.?\,?', text_node_strings):
                docket_numbers.append(
                    self._sanitize_docket_string(text_node_strings))
        return docket_numbers

    def _sanitize_docket_string(self, raw_docket_string):
        """Handle typos and non-standard docket number strings

        Dockets on this page should be in format of "No. #",
        but sometimes they forget the period, or use a comma
        instead.  Stanrdize all to use period, then all of the
        "No. " will be stripped off via the global docket sanitation.
        Regex in _get_docket_numbers() may have to be adjusted if they
        come up with new typos.
        """
        if 'No.' not in raw_docket_string:
            return raw_docket_string.replace('No ', 'No.').replace('No,', 'No.')
        return raw_docket_string

    def _row_contains_date(self, row):
        try:
            self.date = convert_date_string(self._date_row_data_to_string(row))
        except ValueError:
            return False
        return True

    def _row_contains_opinion(self, row):
        return row.xpath('./td[4]') and row.xpath(
            './%s' % self.DOWNLOAD_URL_SUB_PATH)

    def _date_row_data_to_string(self, row):
        return html.tostring(row, method='text', encoding='unicode').strip()

