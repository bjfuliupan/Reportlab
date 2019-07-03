# -*- coding: utf-8 -*-

from reportlab.graphics.shapes import *
from reportlab.graphics import renderPDF

from ReportLabLineCharts import ReportLabHorizontalLineChart
from ReportLabBarCharts import ReportLabVerticalBarChart, ReportLabHorizontalBarChart
from ReportLabPieCharts import ReportLabPieChart


def drawSamplePDF():
    drawing = Drawing(500, 1000)

    lc_cats1 = ["一月", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
    lc_values1 = [(13, 5, 20, 22, 37, 45, 19, 4), (5, 20, 46, 38, 23, 21, 6, 14), (67, 88, 98, 13, 68, 109, 110, 120),
                  (6, 9, 77, 88, 91, 130, 135, 125)]
    lc_cats2 = ["刘攀", "lijie", "longhui", "zijian", "gaofeng", "yilin", "heng", "xuesong"]
    lc_values2 = [(170, 165, 167, 172, 176, 180, 160, 166), (60, 65, 55, 58, 70, 72, 68, 80)]
    bc_cats1 = ["刘攀", "lijie", "longhui", "zijian", "gaofeng", "yilin", "heng", "xuesong"]
    bc_values1 = [(170, 165, 167, 172, 176, 180, 160, 166), (60, 65, 55, 58, 70, 72, 68, 80)]
    bc_cats2 = ["刘攀", "lijie", "longhui", "zijian", "gaofeng", "yilin", "heng", "xuesong"]
    bc_values2 = [(170, 165, 167, 172, 176, 180, 160, 166), (60, 65, 55, 58, 70, 72, 68, 80)]
    pc_cats1 = ["刘攀", "lijie", "longhui", "zijian", "gaofeng", "yilin", "heng", "xuesong"]
    pc_values1 = [170, 165, 167, 172, 176, 180, 160, 166]

    my_line_charts1 = ReportLabHorizontalLineChart(50, 800, 400, 125, lc_cats1, lc_values1,
                                                   legend_names=["乒乓球", "篮球", "排球", "足球"],
                                                   legend_position="bottom-mid",
                                                   main_title="刘攀 first PDF Test.",
                                                   main_title_font_color=colors.blue,
                                                   x_desc="月份", y_desc="数量（个）")
    my_line_charts2 = ReportLabHorizontalLineChart(50, 600, 400, 125, lc_cats2, lc_values2,
                                                   legend_names=["身高", "体重"],
                                                   legend_position="bottom-mid",
                                                   main_title="刘攀 second PDF Test.",
                                                   x_desc="姓名", y_desc="身高/体重")
    my_bar_charts1 = ReportLabVerticalBarChart(50, 400, 150, 125, bc_cats1, bc_values1,
                                               x_desc="姓名", y_desc="身高/体重", label_format="%s",
                                               legend_names=["身高", "体重"])
    my_bar_charts2 = ReportLabHorizontalBarChart(275, 400, 150, 125, bc_cats2, bc_values2, style="stacked",
                                                 x_desc="身高/体重", y_desc="姓名", label_format="%s",
                                                 legend_names=["身高", "体重"])
    my_pie_charts1 = ReportLabPieChart(50, 175, 150, 150, pc_cats1, pc_values1)

    drawing.add(my_line_charts1)
    drawing.add(my_line_charts2)
    drawing.add(my_bar_charts1)
    drawing.add(my_bar_charts2)
    drawing.add(my_pie_charts1)

    renderPDF.drawToFile(drawing, 'example_charts.pdf')


if __name__ == "__main__":
    drawSamplePDF()
