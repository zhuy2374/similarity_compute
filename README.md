### 基于家系的相似度计算工具

#### 使用步骤

1. 安装**uv**，下载**python3.12**：

   ```shell
   # 安装uv包管理工具
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # 下载python3.12
   uv python install 3.12
   ```

2. 同步依赖：

   ```shell
   uv sync
   ```

3. 使用uv执行脚本**.\scripts\run_compute_similarity.py**

   ```shell
   uv run .\scripts\run_compute_similarity.py "你的根目录"
   ```

   #### 参数说明：

   ##### run_compute_similarity.py：
   
   |    参数    |                 说明                 |
   | :--------: | :----------------------------------: |
   |  root_dir  | 存放测序结果的根路径，包含了多个个体 |
   | --with_5mc |           是否计算5mc结果            |
   | --save_csv |            保存至csv文件             |
   | --save_tsv |            保存至tsv文件             |
   |   --sort   |             启用结果排序             |
   
   **run_compute_similarity_use_ped.py**：
   
   |     参数      |                 说明                 |
   | :-----------: | :----------------------------------: |
   |   root_dir    | 存放测序结果的根路径，包含了多个个体 |
   |  --with_5mc   |           是否计算5mc结果            |
   |  --save_csv   |            保存至csv文件             |
   | --family_list |             ped文件路径              |
   |    --sort     |             启用结果排序             |
   
   **run_filter_analyzed_parent_ids.py**：
   
   |        参数        |      说明      |
   | :----------------: | :------------: |
   | offspring_data_dir | 子代数据文件夹 |
   |  parent_data_dir   |  亲代数据目录  |
   |     output_dir     |    输出目录    |
   
   

