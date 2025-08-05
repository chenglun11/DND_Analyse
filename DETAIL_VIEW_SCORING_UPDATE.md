# DetailView 评分标准更新总结

## 更新概述

成功更新了DetailView.vue，使其支持从HomeView传递的评分标准信息，并显示相应的评分结果。

## 主要修改

### 1. 路由参数传递
在HomeView中，查看详情时传递评分标准信息：
```typescript
router.push({ 
  name: 'detail', 
  params: { 
    name: result.name,
    filename: uploadedFiles.value.find(f => f.name.replace('.json', '') === result.name)?.name || result.name + '.json',
    fileId: result.fileId
  },
  query: {
    scoringStandard: selectedScoringStandard.value,
    scoringOptions: JSON.stringify(getCurrentScoringOptions())
  }
})
```

### 2. DetailView接收评分标准
```typescript
// 评分标准相关状态
const scoringStandard = ref<string>('comprehensive')
const scoringOptions = ref<AnalysisOptions>({
  accessibility: true,
  geometric_balance: true,
  loop_ratio: true,
  dead_end_ratio: true,
  treasure_distribution: true,
  monster_distribution: true,
  degree_variance: true,
  door_distribution: true,
  key_path_length: true,
  path_diversity: true
})

// 从路由获取评分标准信息
const getScoringInfoFromRoute = () => {
  const routeScoringStandard = route.query.scoringStandard as string
  const routeScoringOptions = route.query.scoringOptions as string
  
  if (routeScoringStandard) {
    scoringStandard.value = routeScoringStandard
  }
  
  if (routeScoringOptions) {
    try {
      const parsedOptions = JSON.parse(routeScoringOptions)
      scoringOptions.value = parsedOptions
    } catch (error) {
      console.warn('解析评分选项失败:', error)
    }
  }
}
```

### 3. 前端总分计算
在DetailView中使用与HomeView相同的计算算法：
```typescript
// 前端计算总分（与HomeView保持一致）
const calculateFrontendScore = (detailedScores: Record<string, { score: number; detail?: any }>, options: AnalysisOptions): number => {
  // 按类别分组计算
  const structuralMetrics = ['accessibility', 'degree_variance', 'door_distribution', 'dead_end_ratio', 'key_path_length', 'loop_ratio', 'path_diversity']
  const gameplayMetrics = ['treasure_distribution', 'monster_distribution']
  const aestheticMetrics = ['geometric_balance']
  
  // 等权融合各类别分数
  const totalScore = (structuralAvg + gameplayAvg + aestheticAvg) / categoryCount
  
  return Math.round(totalScore * 100) / 100
}
```

### 4. 界面显示评分标准
在分析结果部分添加评分标准信息卡片：
```vue
<!-- 评分标准信息 -->
<div class="scoring-info-card">
  <h3>{{ t('home.scoringStandard') }}</h3>
  <div class="scoring-info">
    <div class="scoring-standard">
      <span class="label">{{ t('detail.scoringStandard') }}:</span>
      <span class="value">{{ t(`home.scoringStandards.${scoringStandard}.name`) }}</span>
    </div>
    <div class="scoring-description">
      {{ t(`home.scoringStandards.${scoringStandard}.description`) }}
    </div>
  </div>
</div>
```

### 5. 样式设计
添加了评分标准信息卡片的样式：
```css
.scoring-info-card {
  background: #f0f4ff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
}

.scoring-standard .value {
  color: #667eea;
  font-weight: 600;
}
```

## 国际化支持

### 中文翻译
```typescript
detail: {
  // ... 其他翻译
  scoringStandard: '评分标准'
}
```

### 英文翻译
```typescript
detail: {
  // ... 其他翻译
  scoringStandard: 'Scoring Standard'
}
```

## 功能特点

### 1. 一致性
- DetailView使用与HomeView相同的评分计算算法
- 确保总分显示的一致性

### 2. 信息传递
- 通过URL query参数传递评分标准信息
- 支持页面刷新后保持评分标准信息

### 3. 用户体验
- 在详情页面显示当前使用的评分标准
- 用户可以清楚了解评分依据

### 4. 错误处理
- 解析评分选项失败时的错误处理
- 默认使用综合评估标准

## 测试验证

1. ✅ 构建成功，无编译错误
2. ✅ 路由参数传递正常
3. ✅ 评分标准信息显示正确
4. ✅ 前端总分计算与HomeView一致
5. ✅ 国际化翻译完整

## 使用流程

1. 在HomeView选择评分标准（如"结构评估"）
2. 上传并分析地下城文件
3. 点击"查看详情"
4. DetailView显示选择的评分标准信息
5. 总分根据选择的评分标准重新计算
6. 用户可以清楚了解评分依据

## 总结

成功实现了DetailView与HomeView的评分标准一致性，确保用户在不同页面看到的总分是基于相同的评分标准计算的。特别适合您提到的需求：**有些设计只想对blank的图进行设计** - 现在从HomeView选择"结构评估"标准后，DetailView也会显示相应的评分标准信息，并基于该标准计算总分。 