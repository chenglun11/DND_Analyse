from cvat_sdk.api_client import Configuration, ApiClient
from cvat_sdk.api_client.models import LabeledShapeRequest, ShapeType
from cvat_sdk.api_client.models import JobAnnotationsUpdateRequest

# 1) set up your client
config = Configuration(host="http://localhost:8080", username="MaxLi", password="Chenganli0717")
with ApiClient(config) as api_client:

    job_id = 1

    # 2) fetch existing annotations
    annotation_data, _ = api_client.jobs_api.retrieve_annotations(job_id)
    old_shapes = annotation_data.shapes

    # 3) build a new list, converting rectangles → polygons
    new_shapes = []
    for s in old_shapes:
        if s.type == ShapeType("rectangle"):
            # s.points = [xtl, ytl, xbr, ybr]
            xtl, ytl, xbr, ybr = s.points
            # polygon as 4 corners (must be in the same order CVAT expects)
            poly_pts = [xtl, ytl, xbr, ytl, xbr, ybr, xtl, ybr]
            new_shapes.append(LabeledShapeRequest(
                type=ShapeType("polygon"),
                frame=s.frame,
                label_id=s.label_id,
                points=poly_pts,
                z_order=s.z_order,
                group=s.group,
                attributes=s.attributes,     # carry over any per-shape attributes
            ))
        else:
            # keep non-rectangles as is
            new_shapes.append(LabeledShapeRequest(
                type=s.type,
                frame=s.frame,
                label_id=s.label_id,
                points=s.points,
                z_order=s.z_order,
                group=s.group,
                attributes=s.attributes,
            ))

    payload = JobAnnotationsUpdateRequest(
        version=annotation_data.version,    # keep the same version to avoid race conditions
        shapes=new_shapes,                  # your list of LabeledShapeRequest
        tags=annotation_data.tags,          # carry over any image-level tags, if present
        tracks=annotation_data.tracks       # carry over any tracks, if present
    )

    # 2. Push it back to CVAT
    api_client.jobs_api.update_annotations(
        job_id,
        job_annotations_update_request=payload
    )