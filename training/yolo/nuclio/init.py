def init_context(context):
    try:
        # 加载配置文件
        with open("/opt/nuclio/function.yaml") as f:
            config = yaml.safe_load(f)
            labels = json.loads(config["metadata"]["annotations"]["spec"])
        
        # 加载模型
        model = YOLO('/opt/nuclio/best.pt')
        
        # 保存到上下文
        context.user_data.model = model
        context.user_data.labels = labels
        
    except Exception as e:
        context.logger.error(f"初始化失败: {str(e)}")
        raise
    
def handler(context, event):
    # 解码图像
    img_bytes = base64.b64decode(event.body["image"])
    img = Image.open(io.BytesIO(img_bytes))
    
    # 执行推理
    results = context.user_data.model(img)
    
    # 处理结果
    detections = []
    for result in results:
        if result.boxes.conf[0] > threshold:
            elements = []
            for idx, kpt in enumerate(result.keypoints.data[0]):
                elements.append({
                    "label": context.user_data.labels[0]["sublabels"][idx]["name"],
                    "points": [float(kpt[0]), float(kpt[1])],
                    "confidence": str(kpt[2])
                })
            
            detections.append({
                "label": "person",
                "type": "skeleton",
                "elements": elements
            })
    
    return context.Response(body=json.dumps(detections))