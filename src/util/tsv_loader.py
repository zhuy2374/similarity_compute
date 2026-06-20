#
# @Author  : zhuy
# @Date    : 2026/1/10 17:23
# @Desc    : tsv加载工具类
#

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


class TSVLoader:
    """
    TSV 文件加载工具类
    """

    @staticmethod
    def load(file_path, row_filters=None, col_filters=None, logic='AND', **kwargs):
        """
        :param file_path: 文件路径
        :param logic: 组合方式
        :param row_filters: 行过滤器列表 (返回 Mask)
        :param col_filters: 列操作列表 (返回处理后的 DF)
        """
        kwargs.setdefault('sep', '\t')
        df = pd.read_csv(file_path, **kwargs)

        # A. 先处理行过滤
        if row_filters:
            if logic.upper() == 'AND':
                mask = pd.Series([True] * len(df), index=df.index)
                for f in row_filters: mask &= f(df)
            else:
                mask = pd.Series([False] * len(df), index=df.index)
                for f in row_filters: mask |= f(df)
            df = df[mask]

        # B. 再处理列筛选/排除
        if col_filters:
            for f in col_filters:
                df = f(df)

        return df


