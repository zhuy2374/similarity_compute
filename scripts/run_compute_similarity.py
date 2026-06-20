#
# @Author  : zhuy
# @Date    : 2026/1/10 20:07
# @Desc    : 相似度计算脚本
#
import argparse
from pathlib import Path
import logging
import sys
import os

from tqdm import tqdm
# 获取项目根目录路径，并将其插入到系统路径的开头，以便能够导入项目中的模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.modules.family_mapper import FamilyMapper
from src.modules.offspring_parent_similarity_calculator import OffspringParentSimilarityCalculator
from src.util.file_util import FileUtil
from src.util.tsv_filters import column_not_contains, drop_columns, fast_assign, column_not_nan

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description="Collect family directories named <familyID>_<individual>.")
    parser.add_argument("root_dir", help="根目录，包含若干以 <家系ID>_<个体> 命名的子文件夹", type=str)
    parser.add_argument("--with_5mc", action="store_true", help="是否计算5mc结果")
    parser.add_argument("--save_csv", action="store_true", help="保存到csv文件",default= True)
    parser.add_argument("--save_tsv", action="store_true", help="保存到tsv文件")
    parser.add_argument("--sort", action="store_true", help="是否对结果排序")
    args = parser.parse_args()

    try:

        base_dir = args.root_dir

        logging.info(f"开始处理根目录：{base_dir}")
        # 统计根目录下的家系
        family_dict = FamilyMapper.collect_family_dirs(root=Path(base_dir), return_absolute=True)
        logging.info(f"处理完成，共有家系：{len(family_dict)}个")

        # 定义过滤器
        row_filters = [
            # 过滤行
            column_not_contains('#chr', ','),
            # 过滤 tvr_consensus 为 NaN 的 行
            column_not_nan('tvr_consensus'),
        ]
        col_filters = [
            # 去掉不用的列
            drop_columns(["position", "ref_samp", "supporting_reads"]),
            # 添加动态列
            fast_assign(
                reads_number=lambda x: x['read_TLs'].str.split(",").str.len()
            )
        ]
        logging.info("开始处理家系数据......")

        # 遍历每个家系
        for key, value in tqdm(family_dict.items(), total=len(family_dict), desc="正在处理家系数据"):
            # 获取dataframe
            s1_df, p1_df, fa_df, mo_df = FileUtil.get_family_dfs(key, base_dir, row_filters, col_filters, with_5mc=args.with_5mc)

            # 计算s1与parent的相似度
            s1_similarity_result_df = OffspringParentSimilarityCalculator.compute_similarity(s1_df, mo_df, fa_df)

            # 计算p1与parent的相似度
            p1_similarity_result_df = OffspringParentSimilarityCalculator.compute_similarity(p1_df, mo_df, fa_df)

            if args.save_csv:
                if args.with_5mc:
                    FileUtil.write_dataframe_to_csv(s1_similarity_result_df, Path(f"{base_dir}/{key}_s1/{key}_s1_5mc_similarity.csv"), sort=args.sort)
                    FileUtil.write_dataframe_to_csv(p1_similarity_result_df, Path(f"{base_dir}/{key}_p1/{key}_p1_5mc_similarity.csv"), sort=args.sort)
                else:
                    FileUtil.write_dataframe_to_csv(s1_similarity_result_df, Path(f"{base_dir}/{key}_s1/{key}_s1_similarity.csv"), sort=args.sort)
                    FileUtil.write_dataframe_to_csv(p1_similarity_result_df, Path(f"{base_dir}/{key}_p1/{key}_p1_similarity.csv"), sort=args.sort)

            if args.save_tsv:
                if args.with_5mc:
                    FileUtil.write_dataframe_to_tsv(s1_similarity_result_df, Path(f"{base_dir}/{key}_s1/{key}_s1_5mc_similarity.tsv"), sort=args.sort)
                    FileUtil.write_dataframe_to_tsv(p1_similarity_result_df, Path(f"{base_dir}/{key}_p1/{key}_p1_5mc_similarity.tsv"), sort=args.sort)
                else:
                    FileUtil.write_dataframe_to_tsv(s1_similarity_result_df, Path(f"{base_dir}/{key}_s1/{key}_s1_similarity.tsv"), sort=args.sort)
                    FileUtil.write_dataframe_to_tsv(p1_similarity_result_df, Path(f"{base_dir}/{key}_p1/{key}_p1_similarity.tsv"), sort=args.sort)

        logging.info("处理完成")
        if args.save_csv:
            logging.info("所有结果已保存至csv")

        if args.save_tsv:
            logging.info("所有结果已保存至tsv")

    except Exception as e:
        logging.error(f"处理数据时出错：{e}")
        return


if __name__ == "__main__":
    main()