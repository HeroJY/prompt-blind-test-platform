当前目录用于保存 Prompt 图片等本地上传文件。

当前实现中：

1. Prompt 图片会保存到 `prompts/` 子目录
2. `tasks.json` 中只保存图片元数据和访问路径
3. 删除任务时会同步清理对应的 Prompt 图片目录
