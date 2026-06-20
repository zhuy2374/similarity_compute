#
# @Author  : zhuy
# @Date    : 2026/1/13 17:44
# @Desc    : 基于ped文件的家系相似度计算脚本
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

from src.util.tsv_loader import TSVLoader
from src.modules.offspring_parent_similarity_calculator import OffspringParentSimilarityCalculator
from src.util.file_util import FileUtil
from src.util.tsv_filters import column_not_contains, drop_columns, fast_assign, column_not_nan

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description="Collect family directories named <familyID>_<individual>.")
    parser.add_argument("root_dir", help="根目录，包含若干以 <家系ID>_<个体> 命名的子文件夹", type=str)
    parser.add_argument("--family_list", help="包含家系代码的文件", type=str)
    parser.add_argument("--with_5mc", action="store_true", help="是否计算5mc结果")
    parser.add_argument("--save_csv", action="store_true", help="保存到csv文件",default= True)
    parser.add_argument("--save_tsv", action="store_true", help="保存到tsv文件")
    parser.add_argument("--sort", action="store_true", help="是否对结果排序")
    args = parser.parse_args()

    try:
        base_dir = args.root_dir

        logging.info(f"开始处理根目录：{base_dir}")

        # 解析ped格式文件
        ped_df = FileUtil.load_ped_file(args.family_list)

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
        # 遍历每个个体
        for _, row in tqdm(ped_df.iterrows(), total=len(ped_df), desc="正在处理家系数据"):
            offspring = row['IID']
            mo = row['MID']
            fa = row['PID']
            # 跳过亲代
            if str(mo) == "0" and str(fa) == "0":
                continue

            offspring_path = f"{base_dir}/{offspring}/{offspring}{'_5mc_telo_out' if args.with_5mc else '_telo_out'}/tlens_by_allele.tsv"
            mo_path = f"{base_dir}/{mo}/{mo}{'_5mc_telo_out' if args.with_5mc else '_telo_out'}/tlens_by_allele.tsv"
            fa_path = f"{base_dir}/{fa}/{fa}{'_5mc_telo_out' if args.with_5mc else '_telo_out'}/tlens_by_allele.tsv"

            offspring_df = TSVLoader.load(Path(offspring_path), row_filters, col_filters)
            mo_df = TSVLoader.load(Path(mo_path), row_filters, col_filters)
            fa_df = TSVLoader.load(Path(fa_path), row_filters, col_filters)

            result_df = OffspringParentSimilarityCalculator.compute_similarity(offspring_df, mo_df, fa_df)

            if args.save_csv:
                if args.with_5mc:
                    FileUtil.write_dataframe_to_csv(result_df, Path(f"{base_dir}/{offspring}/{offspring}_5mc_similarity.csv"), sort=args.sort)
                else:
                    FileUtil.write_dataframe_to_csv(result_df, Path(f"{base_dir}/{offspring}/{offspring}_similarity.csv"), sort=args.sort)

            if args.save_tsv:
                if args.with_5mc:
                    FileUtil.write_dataframe_to_tsv(result_df, Path(f"{base_dir}/{offspring}/{offspring}_5mc_similarity.tsv"), sort=args.sort)
                else:
                    FileUtil.write_dataframe_to_tsv(result_df, Path(f"{base_dir}/{offspring}/{offspring}_similarity.tsv"), sort=args.sort)

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