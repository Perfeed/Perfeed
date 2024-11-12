import json
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PRType(str, Enum):
    bug_fix = "Bug fix"
    tests = "Tests"
    enhancement = "Enhancement"
    documentation = "Documentation"
    other = "Other"


class FileDescription(BaseModel):
    filename: str = Field(description="The full file path of the relevant file.")
    language: str = Field(description="The programming language of the relevant file.")
    changes_summary: str = Field(
        description="a concise summary of the changes in the relevant file, describing in 1-3 sentences."
    )
    changes_title: str = Field(
        description="an informative title for the changes in the files, describing its main theme (5-10 words)."
    )
    label: str = Field(
        description="a single semantic label that represents a type of code changes that occurred in the File. Possible values (partial list): 'bug fix', 'tests', 'enhancement', 'documentation', 'error handling', 'configuration changes', 'dependencies', 'formatting', 'miscellaneous', ..."
    )


class CommentThread(BaseModel):
    parent_thread_id: int = Field(description="parent_thread_id")
    child_thread_ids: list[int] = Field(description="child_thread_ids")
    users: list[str] = Field(description="list all the users involved in the discussion")
    html_url: str = Field(description="the url of the main comment")    
    summary: str = Field(
        description="provide the context and summerize what the comment thread tries to address"
    )
    details: str = Field(
        description="parse comment['body'] to provide user conversation details in plain text and in a 3rd person view"
    )
    eval_aspect: list[str] = Field(
        description="which evaluation cateogry the comment fall into?"
    )
    lead_to_action: str = Field(
        description="review pr comment code_change object and the discussion. determine which of the following: code change, clarification or no action"
    )
    lead_to_action_desc: str = Field(
        description="provide description on lead_to_action field"
    )


class PRSummary(BaseModel):
    type: list[PRType] = Field(
        description="one or more types that describe the PR content. Return only the members of PRType Enum."
    )
    title: str = Field(
        description="an informative title for the PR, describing its main theme"
    )
    description: str = Field(
        description="an informative and concise description of the PR. Highlight the most significant changes."
    )
    pr_files: list[FileDescription] = Field(
        max_length=15,
        description="a list of the files in the PR, and summary of their changes",
    )
    comments: list[CommentThread] = Field(
        max_length=100,
        description="a list of the comment thread in the PR.",
    )

    @classmethod
    def to_json_schema(cls) -> str:
        return json.dumps(cls.model_json_schema(), indent=2)


class PRSummaryMetadata(BaseModel):
    "for metadata purpose. separated from PRSummary. which serves for not only as a data model but a prompt."
    repo: str
    author: str
    pr_number: int
    llm_provider: str
    model: str
    pr_created_at: str
    pr_merged_at: Optional[str] = None
    created_at: str
