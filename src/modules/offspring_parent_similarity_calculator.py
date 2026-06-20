#
# @Author  : zhuy
# @Date    : 2026/1/10 22:05
# @Desc    : 亲代子代相似性计算器
#
import pandas as pd
from pandas import DataFrame
from src.modules.simillarity_calculator import SimilarytiCalculator


class OffspringParentSimilarityCalculator:
    @staticmethod
    def compute_similarity(offspring_df: DataFrame, mo_df: DataFrame, fa_df: DataFrame):
        """
        计算亲代子代相似度
        :param offspring_df: 子代数据
        :param mo_df: 母亲数据
        :param fa_df: 父亲数据
        :return:
        """

        # 构建结果dataframe
        result_df = DataFrame(columns=['number', 'chr', 'offspring_allele_id',
                                       'offspring_TL_p75', 'offspring_reads_numer', 'offspring_tvr_len',
                                       'offspring_tvr_consensus', 'parent','parent_allele_id','parent_TL_p75',
                                       'parent_reads_numer', 'parent_tvr_len', 'parent_tvr_consensus',
                                       'similarity'
                                       ])
        # 计数器, 用于记录 number 字段
        counter = 1

        # 结果数据
        rows = []

        # 读取子代的每一行数据
        for _, offspring in offspring_df.iterrows():
            chr = offspring['#chr']
            # 找到mo_df中所有#chr 为 chr 的行
            mo_rows = mo_df[mo_df['#chr'] == chr]
            # 找到fa_df中所有#chr 为 chr 的行
            fa_rows = fa_df[fa_df['#chr'] == chr]

            # 计算与母亲端粒的相似度
            for _, mo in mo_rows.iterrows():
                # 计算相似度, 保留 4 位小数
                similarity = SimilarytiCalculator.calculate_similarity(offspring['tvr_consensus'], mo['tvr_consensus'], 4)
                # 向 rows 添加数据
                mo_data = {
                    'number': counter,
                    'chr': chr,
                    'offspring_allele_id': offspring['allele_id'],
                    'offspring_TL_p75': offspring['TL_p75'],
                    'offspring_reads_numer': offspring['reads_number'],
                    'offspring_tvr_len': offspring['tvr_len'],
                    'offspring_tvr_consensus': offspring['tvr_consensus'],
                    'parent': 'mo',
                    'parent_allele_id': mo['allele_id'],
                    'parent_TL_p75': mo['TL_p75'],
                    'parent_reads_numer': mo['reads_number'],
                    'parent_tvr_len': mo['tvr_len'],
                    'parent_tvr_consensus': mo['tvr_consensus'],
                    'similarity': similarity,
                }
                rows.append(pd.DataFrame([mo_data]))
                counter += 1

            # 计算与父亲端粒的相似度
            for _, fa in fa_rows.iterrows():
                similarity = SimilarytiCalculator.calculate_similarity(offspring['tvr_consensus'], fa['tvr_consensus'], 4)
                fa_data = {
                    'number': counter,
                    'chr': chr,
                    'offspring_allele_id': offspring['allele_id'],
                    'offspring_TL_p75': offspring['TL_p75'],
                    'offspring_reads_numer': offspring['reads_number'],
                    'offspring_tvr_len': offspring['tvr_len'],
                    'offspring_tvr_consensus': offspring['tvr_consensus'],
                    'parent': 'fa',
                    'parent_allele_id': fa['allele_id'],
                    'parent_TL_p75': fa['TL_p75'],
                    'parent_reads_numer': fa['reads_number'],
                    'parent_tvr_len': fa['tvr_len'],
                    'parent_tvr_consensus': fa['tvr_consensus'],
                    'similarity': similarity,
                }
                rows.append(pd.DataFrame([fa_data]))
                counter += 1

        if rows:
            result_df = pd.concat(rows, ignore_index=True)
        else:
            result_df = pd.DataFrame(columns=result_df.columns)

        return result_df

