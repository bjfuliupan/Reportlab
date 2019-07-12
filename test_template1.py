# -*- coding: utf-8 -*-

import os
from pdflib.PDFTemplate import PDFTemplate


def test_pdf():
    # 读取PDF模板文件
    tpl = os.path.join(os.getcwd(), "templates", "template1.xml")
    template = PDFTemplate.read_template(tpl)
    if template is None:
        print("读取模板文件失败！")
        return

    try:
        # 模板中的所有页
        pages = template['pages']

        # 设置标题显示内容
        PDFTemplate.set_text_data(pages, 0, "title", "刘攀的第一个PDF测试文档2")

        # 设置描述说明内容
        description = ("的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       "刘攀的第一个PDF测试文档。第1行我们导入Paragraph和SimpleDocTemplate类。"
                       "Paragraph是用于生成文本段落的。SimpleDocTemplate是文档布局模板。从上面的例子可以"
                       "看到通过文档模板及样式可以让我们方便的创建面向对象的应用，而不用再关心坐标、绘制命"
                       "令等底层的东西，从而可以方便我们的文档生成。打开hello.pdf看一看效果吧。这回就象是"
                       "真正的文档，\"Hello\"放在上面了。"
                       )
        PDFTemplate.set_paragraph_data(pages, 0, "description", description)

        # 设置折线图的数据
        PDFTemplate.set_line_chart_data(pages, 0, "line_chart",
                                        [(13, 5, 20, 22, 37, 45, 19, 4, 13, 5, 20, 22, 37, 45, 19, 4, 13, 5, 20, 22, 37, 45, 19, 4),
                                  (5, 20, 46, 38, 23, 21, 6, 14, 5, 20, 46, 38, 23, 21, 6, 14, 5, 20, 46, 38, 23, 21, 6, 14),
                                  (67, 88, 98, 13, 68, 109, 110, 120, 67, 88, 98, 13, 68, 109, 110, 120, 67, 88, 98, 13, 68, 109, 110, 120),
                                  (6, 9, 77, 88, 91, 130, 135, 125, 6, 9, 77, 88, 91, 130, 135, 125, 6, 9, 77, 88, 91, 130, 135, 125),
                                  (
                                  13, 5, 20, 22, 37, 45, 19, 4, 13, 5, 20, 22, 37, 45, 19, 4, 13, 5, 20, 22, 37, 45, 19,
                                  4),
                                  (5, 20, 46, 38, 23, 21, 6, 14, 5, 20, 46, 38, 23, 21, 6, 14, 5, 20, 46, 38, 23, 21, 6,
                                   14),
                                  (67, 88, 98, 13, 68, 109, 110, 120, 67, 88, 98, 13, 68, 109, 110, 120, 67, 88, 98, 13,
                                   68, 109, 110, 120),
                                  (6, 9, 77, 88, 91, 130, 135, 125, 6, 9, 77, 88, 91, 130, 135, 125, 6, 9, 77, 88, 91,
                                   130, 135, 125),
                                  (
                                  13, 5, 20, 22, 37, 45, 19, 4, 13, 5, 20, 22, 37, 45, 19, 4, 13, 5, 20, 22, 37, 45, 19,
                                  4),
                                  (5, 20, 46, 38, 23, 21, 6, 14, 5, 20, 46, 38, 23, 21, 6, 14, 5, 20, 46, 38, 23, 21, 6,
                                   14),
                                  (67, 88, 98, 13, 68, 109, 110, 120, 67, 88, 98, 13, 68, 109, 110, 120, 67, 88, 98, 13,
                                   68, 109, 110, 120),
                                  (6, 9, 77, 88, 91, 130, 135, 125, 6, 9, 77, 88, 91, 130, 135, 125, 6, 9, 77, 88, 91,
                                   130, 135, 125)
                                  ],
            ["一月", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
             "一月", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
             "一月", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
            legend_names=["乒乓球", "篮球", "排球", "足球",
                          "乒乓球", "篮球", "排球", "足球",
                          "乒乓球", "篮球", "排球", "足球"])

        # 设置柱状图的数据
        PDFTemplate.set_bar_chart_data(
            pages, 0, "bar_chart", [(170, 165, 167, 172, 176, 180, 160, 166, 170, 165, 167, 172, 176, 180, 160, 166),
                                    (60, 65, 55, 58, 70, 72, 68, 80, 60, 65, 55, 58, 70, 72, 68, 80)],
            ["刘攀", "立杰", "陇辉", "自建", "高峰", "依琳", "张恒", "雪松",
             "刘攀", "立杰", "陇辉", "自建", "高峰", "依琳", "张恒", "雪松"],
            legend_names=["身高", "体重"])

        # # 设置柱状图的数据
        # PDFTemplate.set_bar_chart_data(
        #     items['bar_chart2'], [(170, 165, 167, 172, 176, 180, 160, 166), (60, 65, 55, 58, 70, 72, 68, 80)],
        #     ["刘攀", "立杰", "陇辉", "自建", "高峰", "依琳", "张恒", "雪松"],
        #     legend_names=["身高", "体重"])

        # 设置柱状图的数据
        PDFTemplate.set_pie_chart_data(pages, 2, "pie_chart", [170, 165, 167, 172, 176, 180, 160, 166],
                                       category_names=["刘攀", "立杰", "陇辉", "自建", "高峰", "依琳", "张恒", "雪松"])

        # 生成PDF文档
        PDFTemplate.draw(template)
    except Exception as err:
        import traceback
        traceback.print_exc()
        print(err)


if __name__ == "__main__":
    test_pdf()
