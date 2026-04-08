from typing import List, Optional
from pydantic import BaseModel

class Comment(BaseModel):
    id: int
    content: str
    replies: Optional[List['Comment']] = None  # Self-nested model

Comment.model_rebuild() #what is this for => This is necessary to allow for the self-referential model. 
                         #It tells Pydantic to rebuild the model after defining it,
                         # which allows it to resolve the reference to itself in the 'replies' field. 
                         # Without this, Pydantic would not be able to properly handle the recursive structure of the Comment model
comment_data = Comment(
    id=1,
    content="This is a comment",
    replies=[
        Comment(
            id=2,
            content="This is a reply to the comment",
            replies=[
                Comment(
                    id=3,
                    content="This is a reply to the reply"
                )
            ]
        )
    ]
)

print(comment_data)