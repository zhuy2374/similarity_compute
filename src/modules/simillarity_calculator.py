#
# @Author  : zhuy
# @Date    : 2026/1/10 18:07
# @Desc    : 序列相似度计算
#


class SimilarytiCalculator:
    """
    序列相似度计算器
    """

    @staticmethod
    def calculate_similarity(seq1, seq2, k):
        """
            计算两个序列字符串在重叠区间的 Levenshtein 相似度（float，范围 [0.0, 1.0]）。
            相似度定义为 1 - (edit_distance / overlap_length)，其中 overlap_length = min(len(seq1), len(seq2)).
            如果 overlap_length == 0，则返回 0.0（与原代码保持一致：无重叠视为完全不相似）。

            参数:
                seq1, seq2: 要比较的两个序列（字符串）。

            返回:
                float: 相似度，1.0 表示完全相同，0.0 表示完全不同或无重叠。

            例子:
                >>> calculate_similarityV2("ACGT", "ACGG")
                0.75   # edit distance=1, overlap=4 -> 1 - 1/4 = 0.75
                >>> calculate_similarityV2("AAAA", "TTTT")
                0.0    # edit distance=4, overlap=4 -> 1 - 4/4 = 0.0
                >>> calculate_similarityV2("", "ACGT")
                0.0    # overlap = 0 -> 返回 0.0
            """
        # 取重叠区间（与你原代码中对重叠部分的处理一致）
        overlap = min(len(seq1), len(seq2))
        if overlap == 0:
            return 0.0

        a = seq1[:overlap]
        b = seq2[:overlap]

        # 快速相等检查
        if a == b:
            return 1.0

        # 确保 b 是较短的那个以减少空间（可选）
        if len(b) > len(a):
            a, b = b, a  # 使 len(a) >= len(b)

        # 滚动数组计算 Levenshtein 编辑距离（只保留两行）
        prev_row = list(range(len(b) + 1))
        for i, ca in enumerate(a, start=1):
            cur_row = [i] + [0] * len(b)
            for j, cb in enumerate(b, start=1):
                cost = 0 if ca == cb else 1
                # 删除：prev_row[j] + 1
                # 插入：cur_row[j-1] + 1
                # 替换：prev_row[j-1] + cost
                cur_row[j] = min(prev_row[j] + 1, cur_row[j - 1] + 1, prev_row[j - 1] + cost)
            prev_row = cur_row

        edit_distance = prev_row[-1]
        relative_distance = edit_distance / overlap  # 与原代码相同的归一化方式
        similarity = 1.0 - relative_distance

        # 保证数值边界
        if similarity < 0.0:
            similarity = 0.0
        elif similarity > 1.0:
            similarity = 1.0

        return round(float(similarity), k)