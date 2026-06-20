#
# @Author  : zhuy
# @Date    : 2026/1/10 21:55
# @Desc    : 文件工具类
#
import os
from pathlib import Path

import pandas as pd
from pandas import DataFrame

from src.util.tsv_loader import TSVLoader

import logging


class FileUtil:

    @staticmethod
    def load_csv(path):
        """
        加载csv文件
        :param path: csv文件路径
        :return: dataframe
        """
        # 1. 检查路径是否存在
        if not os.path.exists(path):
            raise RuntimeError(f"文件未找到: {path}")
        try:
            return pd.read_csv(path)
        except Exception as e:
            raise RuntimeError(f"加载 {path} 出错: {e}")

    @staticmethod
    def load_tsv(path):
        # 1. 检查路径是否存在
        if not os.path.exists(path):
            raise RuntimeError(f"文件未找到: {path}")
        try:
            return TSVLoader.load(path)
        except Exception as e:
            raise RuntimeError(f"加载 {path} 出错: {e}")

    @staticmethod
    def load_ped_file(path):
        """
        加载ped格式文件，并判断文件合法性
        :param path: ped文件路径
        :return: 校验后的dataframe
        """
        if not os.path.exists(path):
            raise RuntimeError(f"文件未找到: {path}")
        # 加载文件
        return pd.read_csv(path, sep=r'\s+', dtype=str)


    @staticmethod
    def get_real_case_path(path_str):
        """
        传入一个路径字符串（可能包含错误的大小写），返回文件系统中存在的真实路径对象。
        如果路径不存在，则抛出 FileNotFoundError。
        """
        path_obj = Path(path_str)
        parts = path_obj.parts

        # 判断是从根路径开始还是当前路径开始
        if path_obj.is_absolute():
            # 在 Windows 上 parts[0] 是盘符 (e.g., 'C:\\')，在 Linux 上是 '/'
            # Windows 的盘符通常不区分大小写，直接作为起点
            current_path = Path(parts[0])
            parts_to_traverse = parts[1:]
        else:
            current_path = Path(".")
            parts_to_traverse = parts

        # 逐级遍历路径组件
        for part in parts_to_traverse:
            # 这里的逻辑是：列出 current_path 下的所有文件/文件夹
            # 寻找一个小写形式与 part 的小写形式一致的项
            found = False

            # 保护机制：如果当前路径不是目录（比如中间某个是文件），无法继续遍历
            if not current_path.is_dir():
                raise FileNotFoundError(f"路径片段 '{current_path}' 不是一个文件夹")

            for child in current_path.iterdir():
                if child.name.lower() == part.lower():
                    current_path = child
                    found = True
                    break

            if not found:
                raise FileNotFoundError(f"未在 '{current_path}' 中找到 '{part}' ")

        return current_path


    @staticmethod
    def get_family_dfs(family_code, root_dir, row_filters, col_filters, with_5mc):
        """
        获取家系下所有样本的dataframe
        :param family_code: 家系编号
        :param root_dir: 家系文件夹根目录
        :param row_filters: 行过滤器
        :param col_filters: 列过滤器
        :param with_5mc: 是否计算5mc
        :return: s1_df, p1_df, fa_df, mo_df
        """

        # 获取tsv文件路径
        if with_5mc:
            s1_tsv_path = FileUtil.get_real_case_path(f"{root_dir}/{family_code}_s1/{family_code}_s1_5mc_telo_out/tlens_by_allele.tsv")
            p1_tsv_path = FileUtil.get_real_case_path(f"{root_dir}/{family_code}_p1/{family_code}_p1_5mc_telo_out/tlens_by_allele.tsv")
            fa_tsv_path = FileUtil.get_real_case_path(f"{root_dir}/{family_code}_fa/{family_code}_fa_5mc_telo_out/tlens_by_allele.tsv")
            mo_tsv_path = FileUtil.get_real_case_path(f"{root_dir}/{family_code}_mo/{family_code}_mo_5mc_telo_out/tlens_by_allele.tsv")
        else:
            s1_tsv_path = FileUtil.get_real_case_path(f"{root_dir}/{family_code}_s1/{family_code}_s1_telo_out/tlens_by_allele.tsv")
            p1_tsv_path = FileUtil.get_real_case_path(f"{root_dir}/{family_code}_p1/{family_code}_p1_telo_out/tlens_by_allele.tsv")
            fa_tsv_path = FileUtil.get_real_case_path(f"{root_dir}/{family_code}_fa/{family_code}_fa_telo_out/tlens_by_allele.tsv")
            mo_tsv_path = FileUtil.get_real_case_path(f"{root_dir}/{family_code}_mo/{family_code}_mo_telo_out/tlens_by_allele.tsv")

        # 读取tsv文件，返回dataframe，可自定义过滤器
        s1_df = TSVLoader.load(s1_tsv_path, row_filters, col_filters)
        p1_df = TSVLoader.load(p1_tsv_path, row_filters, col_filters)
        fa_df = TSVLoader.load(fa_tsv_path, row_filters, col_filters)
        mo_df = TSVLoader.load(mo_tsv_path, row_filters, col_filters)

        return s1_df, p1_df, fa_df, mo_df

    @staticmethod
    def write_dataframe_to_csv(df: DataFrame, path, sort: bool = True):
        if sort:
            # 按照similarity降序
            df = FileUtil.sort_dataframe(df, 'offspring_allele_id', 'similarity', index="number")
        df.to_csv(path, index=False, encoding="utf-8")

    @staticmethod
    def write_dataframe_to_tsv(df: DataFrame, path, sort: bool = True):
        if sort:
            # 按照similarity降序
            df = FileUtil.sort_dataframe(df, 'offspring_allele_id', 'similarity', index="number")
        df.to_csv(path, index=False, encoding="utf-8", sep="\t")


    @staticmethod
    def sort_dataframe(df: DataFrame, group_columns: str, sort_columns:  str, ascending: bool = False, index: str = None) -> DataFrame:
        """
        排序dataframe
        :param df: 要排序的数据
        :param group_columns: 分组字段
        :param sort_columns:  排序字段
        :param ascending: 是否升序排序
        :param index: 序号字段
        :return: 排序后的DataFrame
        """
        df[group_columns] = pd.Categorical(df[group_columns], categories=pd.unique(df[group_columns]), ordered=True)
        df = df.sort_values([group_columns, sort_columns], ascending=[True, ascending])

        # 重置序号（若有）
        if index is not None:
            df[index] = range(1, len(df) + 1)

        # 重置索引
        df = df.reset_index(drop=True)

        return df


