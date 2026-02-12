#!/usr/bin/env python3
"""Custom Fields Filter tools for Sensor Tower MCP Server."""

from typing import Annotated, Optional

from fastmcp import FastMCP
from pydantic import Field

from ..base import SensorTowerTool


class CustomFieldsTools(SensorTowerTool):
    """Tools for Custom Fields Filter API endpoints."""

    category = "CustomFields"

    def register_tools(self, mcp: FastMCP) -> None:
        """Register all custom fields tools with FastMCP."""

        @self.tool(
            mcp,
            name="get_custom_fields_values",
            title="Get Custom Fields Values",
        )
        async def get_custom_fields_values(
            term: Annotated[
                Optional[str],
                Field(description="Search by field names (e.g. 'Revenue', 'Release Date', 'Retention')", default=None),
            ] = None,
        ) -> dict:
            """List all available custom fields and their possible filter values. Use this to discover which filters exist before creating a custom fields filter."""

            params = {}
            if term:
                params["term"] = term

            return await self.make_request(
                "/v1/custom_fields_filter/fields_values",
                params,
            )

        @self.tool(
            mcp,
            name="create_custom_fields_filter",
            title="Create Custom Fields Filter",
            annotations={
                "title": "Create Custom Fields Filter",
                "readOnlyHint": False,
                "idempotentHint": False,
                "openWorldHint": True,
            },
        )
        async def create_custom_fields_filter(
            custom_fields: Annotated[
                str,
                Field(
                    description='JSON array of filter objects. Each object needs: "name" (field name), "global" (true for built-in fields), "values" (array of allowed values). Optional: "exclude" (true to exclude matching values). Example: [{"name": "Earliest Release Date", "global": true, "values": ["2026/01", "2026/02"]}, {"name": "Last 30 Days Revenue (WW)", "global": true, "values": ["5K - 50K", "50K - 100K"]}]'
                ),
            ],
        ) -> dict:
            """Create a reusable custom fields filter and get its ID. Use get_custom_fields_values first to discover valid field names and values. Pass the returned filter ID to get_top_and_trending or usage_top_apps via custom_fields_filter_id."""

            import json
            try:
                fields_list = json.loads(custom_fields)
            except json.JSONDecodeError as e:
                from fastmcp.exceptions import ToolError
                raise ToolError(f"Invalid JSON for custom_fields: {e}")

            return await self.make_post_request(
                "/v1/custom_fields_filter",
                json_body={"custom_fields": fields_list},
            )

        @self.tool(
            mcp,
            name="show_custom_fields_filter",
            title="Show Custom Fields Filter",
        )
        async def show_custom_fields_filter(
            filter_id: Annotated[
                str,
                Field(description="Custom fields filter ID returned by create_custom_fields_filter"),
            ],
        ) -> dict:
            """Show the field names and values of an existing custom fields filter."""

            return await self.make_request(
                f"/v1/custom_fields_filter/{filter_id}",
                {},
            )
