import argparse
import csv
import datetime
import logging
import time

import krxreader.calendar
import krxreader.etf

import config


def save_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(data)


def main(date, is_sort):
    if date is None:
        dt = krxreader.calendar.now()
    else:
        dt = datetime.datetime.strptime(date, '%Y%m%d')
    logging.info(f'dt: {dt}')

    if not krxreader.calendar.is_trading_day(dt):
        logging.warning(f'{dt.strftime('%Y-%m-%d')} is not trading day')
        return

    etf = krxreader.etf.ETF(dt.strftime('%Y%m%d'))

    for code in config.issue_codes:
        (item_name, _, _) = etf.search_issue(code)
        dic_lst = etf.portfolio_deposit_file(code)

        if is_sort:
            dic_lst.sort(key=lambda x: int(x['VALU_AMT'].replace(',', '').replace('-', '0')), reverse=True)

        data = [ [item['COMPST_ISU_NM'], item['COMPST_ISU_CU1_SHRS']] for item in dic_lst ]
        data.insert(0, [dt.strftime('%Y-%m-%d'), item_name])

        save_csv(data, 'etf_pdf_' + code + '_latest.csv')
        time.sleep(config.interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='YYYYMMDD')
    parser.add_argument('--sort', type=bool, default=False)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(f'args: {args}')

    main(args.date, args.sort)
