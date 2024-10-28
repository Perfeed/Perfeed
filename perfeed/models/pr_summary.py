import json
from enum import Enum

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
        description="concise summary of the changes in the relevant file, in bullet points (1-4 bullet points)."
    )
    changes_title: str = Field(
        description="an informative title for the changes in the files, describing its main theme (5-10 words)."
    )
    label: str = Field(
        description="a single semantic label that represents a type of code changes that occurred in the File. Possible values (partial list): 'bug fix', 'tests', 'enhancement', 'documentation', 'error handling', 'configuration changes', 'dependencies', 'formatting', 'miscellaneous', ..."
    )


class CommentDescription(BaseModel):
    id: int = Field(description="comment_id")
    html_url: str = Field(description="the url of the comment")
    summary: str = Field(
        description="provide the context and summerize what the comment tries to address"
    )
    eval_aspect: list[str] = Field(
        description="which evaluation cateogry the comment fall into?"
    )
    lead_to_action: str = Field(
        description="what impact does the comment have? any code change, reply, or no action?"
    )
    lead_to_action_desc: str = Field(
        description="provide description on lead_to_action field"
    )


class PRSummary(BaseModel):
    type: list[PRType] = Field(
        description="one or more types that describe the PR content. Return the label member value (e.g. 'Bug fix', not 'bug_fix')"
    )
    title: str = Field(
        description="an informative title for the PR, describing its main theme"
    )
    description: str = Field(
        description="an informative and concise description of the PR. Use bullet points. Display first the most significant changes."
    )
    pr_files: list[FileDescription] = Field(
        max_length=15,
        description="a list of the files in the PR, and summary of their changes",
    )
    comments: list[CommentDescription] = Field(
        max_length=10,
        description="a list of the comments in the PR. Display first the most useful comments.",
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
    pr_merged_at: str
    created_at: str
