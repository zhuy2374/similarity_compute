#
# @Author  : zhuy
# @Date    : 2026/3/1 16:32
# @Desc    : 过滤掉已经分析的亲代id
#
import argparse
from collections import defaultdict
from pathlib import Path
import logging
import sys
import os
import pandas as pd


from tqdm import tqdm
# 获取项目根目录路径，并将其插入到系统路径的开头，以便能够导入项目中的模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="Filter analyzed parent's ids")
    parser.add_argument("offspring_data_dir", help="子代数据目录", type=str)
    parser.add_argument("parent_data_dir", help="亲代数据目录", type=str)
    parser.add_argument("output_dir", help="输出目录", type=str)
    args = parser.parse_args()

    # 1. 遍历子代数据目录
    offspring_data_dir = args.offspring_data_dir
    offspring_data_dir_path = Path(offspring_data_dir)
    if not offspring_data_dir_path.exists() or not offspring_data_dir_path.is_dir():
        raise ValueError(f"指定路径不存在或不是目录: {offspring_data_dir_path}")

    parent_data_dir_path = Path(args.parent_data_dir)
    if not parent_data_dir_path.exists() or not parent_data_dir_path.is_dir():
        raise ValueError(f"指定路径不存在或不是目录: {parent_data_dir_path}")

    output_dir_path = Path(args.output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    offspring_files = [p for p in offspring_data_dir_path.iterdir() if p.is_file()]
    for p in tqdm(offspring_files, desc="Filtering parent files"):

        # 2. 获取文件名中的家系ID和子代名称
        name_list = p.name.strip().split("_")
        family_id = name_list[0]
        offspring = name_list[1]

        # 3. 读取csv文件，并将parent_allele_id列强制指定为字符串类型
        offspring_df = pd.read_csv(p, dtype={'parent_allele_id': str})
        parent_ids_to_filter = defaultdict(list)

        for index, row in offspring_df.iterrows():
            parent = row['parent']
            parent_allele_id = row['parent_allele_id']
            # 只有当parent_allele_id不为空时，才将其加入待过滤列表
            if parent in ['mo', 'fa'] and pd.notna(parent_allele_id):
                parent_ids_to_filter[parent].append(parent_allele_id)

        for parent, allele_ids_to_filter in parent_ids_to_filter.items():
            # 如果该parent没有任何有效的allele_id需要过滤，则跳过
            if not allele_ids_to_filter:
                continue

            # 3.1. 去亲代文件夹找到对应的文件
            parent_file_name = f"{family_id}_{parent}_5mc_similarity_{offspring}_sorted.csv"
            parent_file_path = parent_data_dir_path / parent_file_name

            if not parent_file_path.exists():
                logging.warning(f"亲代文件不存在，跳过: {parent_file_path}")
                continue

            # logging.info(f"正在{parent_file_name}中过滤以下parent_allele_id:\n {allele_ids_to_filter}的行...")

            # 3.2.打开找到的文件，并将parent_allele_id列强制指定为字符串类型
            parent_df = pd.read_csv(parent_file_path, dtype={'parent_allele_id': str})
            filtered_df = parent_df[~parent_df['parent_allele_id'].isin(allele_ids_to_filter)]

            # 3.3 过滤filtered_df中parent_reads_numer为1的行
            filtered_df = filtered_df[filtered_df['parent_reads_numer'] != 1]

            # 4. 保存过滤后的亲代文件
            output_filename = f"{parent_file_path.stem}_filtered{parent_file_path.suffix}"
            output_path = output_dir_path / output_filename
            filtered_df.to_csv(output_path, index=False)
            # logging.info(f"已保存过滤后的文件: {output_path}")

    logging.info("处理完成...")


if __name__ == "__main__":
    main()