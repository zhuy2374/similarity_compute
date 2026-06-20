#
# @Author  : zhuy
# @Date    : 2026/1/10 20:04
# @Desc    : 从目录中寻找所有家系
#
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


class FamilyMapper:

    @staticmethod
    def collect_family_dirs(
            root: Path,
            recursive: bool = False,
            return_absolute: bool = False,
            require_underscore: bool = True,
    ) -> Dict[str, List[str]]:
        """
        扫描 root 下的子项并按家系ID分组。

        参数:
          root: 要扫描的根目录 (pathlib.Path 或可转为 Path 的字符串)
          recursive: 是否递归搜索所有子目录（默认 False，只扫描第一层）
          return_absolute: value 中返回绝对路径（True）或仅返回目录名（False）
          require_underscore: 是否只接受含 '_' 的名称；若 False，则把没有 '_' 的目录视为 key='' 的项

        返回:
          dict: { family_id: [folders...] }
        """
        root = Path(root)
        if not root.exists() or not root.is_dir():
            raise ValueError(f"指定路径不存在或不是目录: {root}")

        groups = defaultdict(list)

        iterator = root.rglob('*') if recursive else root.iterdir()

        for p in iterator:
            if not p.is_dir():
                continue
            # 只取子目录名，不考虑隐藏目录等过滤策略（可根据需要加）
            name = p.name.strip()
            if require_underscore:
                if '_' not in name:
                    # 跳过不符合 <家系ID>_<个体> 的目录
                    continue
                family_id, _ = name.split('_', 1)
            else:
                parts = name.split('_', 1)
                family_id = parts[0] if parts else ''
            key = family_id
            val = str(p.resolve()) if return_absolute else name
            groups[key].append(val)

        # 按 key 排序并对每个 value 列表排序（可选）
        result = {k: sorted(v) for k, v in sorted(groups.items())}
        return result