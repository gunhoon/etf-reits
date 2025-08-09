import argparse
import csv
import datetime
import logging
import time

import krxfetch.calendar
import krxfetch.fetch


def search_issue(issue_code: str) -> tuple:
    """ETF 종목 검색"""

    payload = {
        'locale': 'ko_KR',
        'mktsel': 'ETF',
        'searchText': issue_code,
        'bld': 'dbms/comm/finder/finder_secuprodisu'
    }
    logging.info(payload)

    dic_lst = krxfetch.fetch.get_json_data(payload)
    first_item = dic_lst[0]

    return (
        first_item['codeName'],
        first_item['short_code'],
        first_item['full_code']
    )


def etf_pdf(date: str, issue_code: str) -> list[list]:
    """[13108] 통계 > 기본 통계 > 증권상품 > ETF > PDF(Portfolio Deposit File)"""

    (item_name, item_code, full_code) = search_issue(issue_code)

    payload = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT05001',
        'locale': 'ko_KR',
        'tboxisuCd_finder_secuprodisu1_0': item_code + '/' + item_name,
        'isuCd': full_code,
        'isuCd2': 'KR7152100004',
        'codeNmisuCd_finder_secuprodisu1_0': item_name,
        'param1isuCd_finder_secuprodisu1_0': '',
        'trdDd': date,
        'share': '1',
        'money': '1',
        'csvxls_isNo': 'false'
    }
    logging.info(payload)

    dic_lst = krxfetch.fetch.get_json_data(payload)
    # keys = list(dic_lst[0])

    # data = [list(item.values()) for item in dic_lst]
    # data.insert(0, keys)

    data = [ [item['COMPST_ISU_NM'], item['COMPST_ISU_CU1_SHRS']] for item in dic_lst ]
    data.insert(0, [item_name, date])

    return data


def save_csv(data, filename):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def main(date):
    if date is None:
        dt = krxfetch.calendar.now()
    else:
        dt = datetime.datetime.strptime(date, '%Y%m%d')

    logging.info(dt)

    if not krxfetch.calendar.is_trading_day(dt):
        logging.warning(f'{dt.strftime('%Y-%m-%d')} is not trading day.')
        return

    reits_list = ['0086B0', '329200', '476800', '429740', '480460']

    for reits in reits_list:
        output = etf_pdf(dt.strftime('%Y%m%d'), reits)
        save_csv(output, 'etf_pdf_' + reits + '_latest.csv')
        time.sleep(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='YYYYMMDD')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    main(args.date)
