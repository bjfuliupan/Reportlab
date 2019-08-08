# -*- coding: utf-8 -*-

from reportlab.platypus import Table


class ReportLabTable(Table):

    def get_row_heights(self):
        self.wrap(1, 1)
        return self._rowHeights
