import os
import sys

import jinja2

from piecash_utilities.report import report, RangeOption, DateOption, StringOption, execute_report


@report(
    title="My default example report [testx]",
    name="default-sample-testx",
    menu_tip="Default sample generated by 'gc_report_create testx'",
    options_default_section="main",
)
def generate_report(
        book_url,
        a_number: RangeOption(
            section="main",
            sort_tag="a",
            documentation_string="This is a number",
            default_value=3),
        a_str: StringOption(
            section="main",
            sort_tag="c",
            documentation_string="This is a string",
            default_value="with a default value"),
        a_date: DateOption(
            section="main",
            sort_tag="d",
            documentation_string="This is a date",
            default_value="(lambda () (cons 'absolute (cons (current-time) 0)))"),
        another_number: RangeOption(
            section="main",
            sort_tag="b",
            documentation_string="This is a number",
            default_value=3)
):
    import piecash

    with piecash.open_book(uri_conn=book_url, readonly=True, open_if_lock=True) as b:

        tpl_name = os.path.basename(__file__).replace("py", "html")
        env = jinja2.Environment(loader=jinja2.PackageLoader(__name__, '.'))

        return env.get_template(tpl_name).render(
            enumerate=enumerate,
            list=list,
            path_report=os.path.abspath(__file__),
            **vars()
        )


if __name__ == '__main__':
    execute_report(generate_report, sys.argv[1])
