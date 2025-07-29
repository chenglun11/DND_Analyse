# 国际化 (i18n) 功能说明

## 概述

本项目已集成 Vue I18n 国际化功能，支持中文和英文两种语言。用户可以通过页面右上角的语言切换器来切换语言。

## 功能特性

- ✅ 支持中文和英文双语
- ✅ 语言切换器组件
- ✅ 语言设置本地存储
- ✅ 响应式设计
- ✅ 完整的翻译覆盖

## 使用方法

### 1. 语言切换

在页面右上角可以看到语言切换器，包含两个按钮：
- **中文** - 切换到中文界面
- **English** - 切换到英文界面

点击任意按钮即可切换语言，设置会自动保存到本地存储。

### 2. 开发中使用翻译

在 Vue 组件中使用翻译：

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 使用翻译
const message = t('common.loading')
</script>

<template>
  <div>
    <h1>{{ t('app.title') }}</h1>
    <p>{{ t('app.subtitle') }}</p>
  </div>
</template>
```

### 3. 添加新的翻译

在 `src/i18n/index.ts` 文件中添加新的翻译：

```typescript
// 中文翻译
const zh = {
  newSection: {
    title: '新标题',
    description: '新描述'
  }
}

// 英文翻译
const en = {
  newSection: {
    title: 'New Title',
    description: 'New Description'
  }
}
```

## 翻译结构

### 通用文本 (common)
- `loading` - 加载中
- `error` - 错误
- `success` - 成功
- `cancel` - 取消
- `confirm` - 确认
- `save` - 保存
- `delete` - 删除
- `edit` - 编辑
- `view` - 查看
- `export` - 导出
- `import` - 导入

### 导航 (nav)
- `home` - 首页
- `test` - 测试
- `about` - 关于
- `help` - 帮助
- `detail` - 详情

### 应用信息 (app)
- `title` - 应用标题
- `subtitle` - 应用副标题
- `description` - 应用描述

### 首页 (home)
- `uploadTitle` - 上传标题
- `uploadDescription` - 上传描述
- `supportedFormats` - 支持格式
- `selectFiles` - 选择文件
- `startAnalysis` - 开始分析
- `analyzing` - 分析中
- `analysisResults` - 分析结果
- `overallScore` - 总体评分
- `viewDetails` - 查看详情
- `exportReport` - 导出报告

### 详情页 (detail)
- `backButton` - 返回按钮
- `backButtonTitle` - 返回按钮标题
- `refreshButton` - 刷新按钮
- `dungeonVisualization` - 地牢可视化
- `canvasVisualization` - Canvas可视化
- `generatedImage` - 生成的可视化图像
- `noVisualizationData` - 没有可视化数据
- `analysisResults` - 分析结果
- `overallScore` - 总体评分
- `detailedMetrics` - 详细指标
- `improvementSuggestions` - 改进建议

### 质量指标 (metrics)
- `accessibility` - 可达性
- `aestheticBalance` - 美学平衡
- `loopRatio` - 环路比例
- `deadEndRatio` - 死胡同比例
- `treasureDistribution` - 宝藏分布
- `monsterDistribution` - 怪物分布
- `degreeVariance` - 度方差
- `doorDistribution` - 门分布
- `keyPathLength` - 关键路径长度
- `pathDiversity` - 路径多样性
- `treasureMonsterDistribution` - 宝藏怪物分布

### 评分等级 (scoreLevels)
- `excellent` - 优秀
- `good` - 良好
- `average` - 一般
- `poor` - 较差

### 错误信息 (errors)
- `fileUploadFailed` - 文件上传失败
- `analysisFailed` - 分析失败
- `networkError` - 网络错误
- `serverError` - 服务器错误
- `unknownError` - 未知错误
- `fileNotSupported` - 不支持的文件格式
- `fileTooLarge` - 文件过大
- `noFilesSelected` - 未选择文件

### 成功信息 (success)
- `fileUploaded` - 文件上传成功
- `analysisCompleted` - 分析完成
- `dataExported` - 数据导出成功
- `settingsSaved` - 设置保存成功

### 确认对话框 (confirm)
- `deleteFile` - 确定要删除这个文件吗？
- `clearAllFiles` - 确定要清除所有文件吗？
- `clearAllResults` - 确定要清除所有结果吗？
- `exportData` - 确定要导出数据吗？

## 技术实现

### 1. 依赖安装

```bash
npm install vue-i18n@next
```

### 2. 配置文件

主要配置文件：`src/i18n/index.ts`

### 3. 组件集成

在 `main.ts` 中集成：

```typescript
import i18n from './i18n'

app.use(i18n)
```

### 4. 语言切换器组件

位置：`src/components/LanguageSwitcher.vue`

功能：
- 显示当前语言
- 提供语言切换按钮
- 自动保存语言设置到 localStorage

## 测试

访问 `/test` 页面可以查看所有翻译内容的测试。

## 注意事项

1. 所有用户界面文本都应该使用翻译函数
2. 新增功能时需要同时添加中英文翻译
3. 翻译键名应该具有描述性和层次结构
4. 语言设置会自动保存到浏览器本地存储

## 扩展支持

如需添加更多语言支持，只需：

1. 在 `src/i18n/index.ts` 中添加新的语言包
2. 在 `LanguageSwitcher.vue` 中添加对应的切换按钮
3. 更新默认语言设置

例如添加日文支持：

```typescript
const ja = {
  // 日文翻译
}

const i18n = createI18n({
  locale: 'zh',
  fallbackLocale: 'en',
  messages: {
    zh,
    en,
    ja  // 添加日文
  }
})
``` 