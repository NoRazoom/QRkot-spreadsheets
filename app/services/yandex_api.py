from datetime import datetime
from typing import List, Dict
import io

import xlsxwriter

from app.core.yandex_client import YandexDiskClient
from app.core.config import settings


def format_time_delta(delta):
    final_str = ''
    if delta.days:
        final_str = f'{delta.days} дн. '
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    final_str += f'{hours} ч. {minutes} мин.'
    return final_str


async def create_simple_report(
        yandex_client: YandexDiskClient,
        projects: List[Dict[str, any]]
):
    now_date_time = datetime.now().strftime(settings.report_format)
    filename = f'отчет_{now_date_time}'.replace(
        ':', '-').replace(' ', '_').replace('/', '-')
    upload_url, file_path = await yandex_client.create_excel_file(filename)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Отчет")

    bold_format = workbook.add_format({'bold': True})
    header_format = workbook.add_format({'bg_color': 'blue', 'bold': True})
    all_format = workbook.add_format({'border': 1})

    worksheet.merge_range('A1:C1', f'отчет от {now_date_time}', bold_format)
    headers = ['Название проекта', 'Время сбора', 'Описание']
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)

    last_row = 2
    for row, project in enumerate(projects, start=2):
        start_time = project['create_date']
        finish_time = project['close_date']
        if finish_time is not None:
            time = finish_time - start_time
            time_str = format_time_delta(time)
        else:
            time_str = 'не завершен'

        worksheet.write(row, 0, str(project['name']), all_format)
        worksheet.write(row, 1, time_str, all_format)
        worksheet.write(row, 2, str(project['description']), all_format)
        last_row = row

    worksheet.merge_range(f'A{last_row + 2}:C{last_row + 2}',
                          f'Итого: {len(projects)} проектов.', bold_format)

    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 30)

    workbook.close()
    output.seek(0)

    await yandex_client.upload_file(upload_url, output.getvalue())
    pub_link = await yandex_client.publish_file(file_path)
    return pub_link
