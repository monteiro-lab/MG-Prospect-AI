from pydantic import BaseModel, ConfigDict

class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    html_body: str

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplateResponse(EmailTemplateBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class EmailPreviewRequest(BaseModel):
    lead_id: int
    template_id: int

class EmailPreviewResponse(BaseModel):
    subject: str
    html_body: str
    text_body: str
    lead_data: dict

class EmailSendRequest(BaseModel):
    lead_id: int
    template_id: int