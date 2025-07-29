# 地下城分析器 (Dungeon Analyzer)

一个专业的D&D地下城质量评估工具，包含Vue.js前端界面和Flask后端API。

## 项目结构

```
dungeon-adapter/
├── frontend/                 # Vue.js前端应用
│   ├── src/
│   │   ├── components/      # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── services/       # API服务
│   │   └── router/         # 路由配置
│   └── package.json
├── flask_backend/           # Flask后端API
│   ├── src/                # 复制的分析模块
│   ├── app.py              # Flask应用主文件
│   ├── run.py              # 启动脚本
│   └── requirements.txt    # Python依赖
├── src/                    # 原始Python分析模块
└── README.md
```

## 功能特性

### 前端功能
- 🎨 现代化的Vue.js界面
- 📁 拖拽文件上传
- 🔍 多种分析选项
- 📊 可视化分析结果
- 🗺️ Phaser.js地下城地图可视化
- 📱 响应式设计

### 后端功能
- 🔌 RESTful API接口
- 📊 多格式地下城文件支持
- 🎯 多种质量评估指标
- 🔄 批量分析处理
- 🌐 跨域支持

## 快速开始

### 1. 启动Flask后端

```bash
cd flask_backend
pip install -r requirements.txt
python app.py
```

后端将在 `http://localhost:5001` 启动

### 2. 启动Vue前端

```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 3. 使用应用

1. 打开浏览器访问 `http://localhost:5173`
2. 上传地下城JSON文件
3. 选择分析选项
4. 点击"开始分析"
5. 查看分析结果

## API接口

### 健康检查
```
GET /api/health
```

### 获取支持格式
```
GET /api/supported-formats
```

### 获取分析选项
```
GET /api/analysis-options
```

### 分析单个文件
```
POST /api/analyze
Content-Type: multipart/form-data
```

### 批量分析
```
POST /api/analyze-batch
Content-Type: multipart/form-data
```

### 格式转换
```
POST /api/convert-dungeon
Content-Type: multipart/form-data
```

## 支持的文件格式

- **Watabou**: Watabou Dungeon Generator格式
- **Donjon**: Donjon Dungeon Generator格式
- **DungeonDraft**: DungeonDraft导出格式
- **Edgar**: Edgar Dungeon Generator格式
- **JSON**: 通用JSON格式

## 分析指标

### 结构性指标
- **可达性**: 分析地下城的可达性和路径设计
- **度方差**: 评估房间连接度的分布
- **门分布**: 分析门的位置和分布
- **死胡同比例**: 评估死胡同的数量和分布
- **关键路径长度**: 分析关键路径的设计
- **环路比例**: 分析环路设计，避免线性体验
- **路径多样性**: 评估路径选择的多样性

### 可玩性指标
- **宝藏怪物分布**: 分析宝藏和怪物的分布合理性

### 视觉性指标
- **美学平衡**: 评估房间布局的美观性和平衡性

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite
- Phaser.js (游戏引擎)
- Vue Router
- Pinia (状态管理)

### 后端
- Flask
- Flask-CORS
- Python 3.x

## 开发说明

### 前端开发
```bash
cd frontend
npm run dev          # 开发模式
npm run build        # 构建生产版本
npm run preview      # 预览构建结果
```

### 后端开发
```bash
cd flask_backend
python app.py        # 开发模式
```

## 注意事项

1. **端口冲突**: 如果5001端口被占用，可以修改`flask_backend/app.py`中的端口号
2. **文件大小**: 上传文件大小限制为16MB
3. **分析时间**: 复杂的地下城可能需要较长的分析时间
4. **浏览器兼容**: 建议使用现代浏览器（Chrome、Firefox、Safari）

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License 