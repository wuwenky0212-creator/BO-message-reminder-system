"""
Organization tree permission filtering algorithm.

This module provides functionality to apply user's organization permissions
to SQL queries, supporting hierarchical organization structures.
"""

from typing import List, Any, Optional
from sqlalchemy.orm import Query
from sqlalchemy import Column, or_

from .jwt_parser import UserContext


class PermissionFilter:
    """
    Permission filter for applying organization tree permissions to SQL queries.
    
    This class handles:
    - Applying org_ids from UserContext to SQL WHERE clauses
    - Supporting hierarchical organization structures
    - Filtering data based on organization tree permissions
    """
    
    def __init__(self):
        """Initialize permission filter."""
        pass
    
    def apply_org_filter(
        self,
        query: Query,
        user_context: UserContext,
        org_id_column: Column
    ) -> Query:
        """
        Apply organization permission filter to SQL query.
        
        This method adds a WHERE clause to filter records based on the user's
        authorized organization IDs. It supports hierarchical organization
        structures where users can access data from their assigned organizations.
        
        Args:
            query: SQLAlchemy Query object to filter
            user_context: User context containing org_ids
            org_id_column: The column to filter on (e.g., Table.org_id)
        
        Returns:
            Query: Filtered query with organization permission applied
        
        Examples:
            >>> from sqlalchemy.orm import Session
            >>> from backend.models import Message
            >>> session = Session()
            >>> query = session.query(Message)
            >>> filter = PermissionFilter()
            >>> filtered_query = filter.apply_org_filter(
            ...     query, user_context, Message.org_id
            ... )
        """
        # If user has no org permissions, return empty result
        if not user_context.org_ids:
            # Return query that will match nothing
            return query.filter(org_id_column.in_([]))
        
        # Apply IN clause for organization IDs
        return query.filter(org_id_column.in_(user_context.org_ids))
    
    def apply_portfolio_filter(
        self,
        query: Query,
        user_context: UserContext,
        portfolio_id_column: Column
    ) -> Query:
        """
        Apply portfolio permission filter to SQL query.
        
        This method adds a WHERE clause to filter records based on the user's
        authorized portfolio IDs.
        
        Args:
            query: SQLAlchemy Query object to filter
            user_context: User context containing portfolio_ids
            portfolio_id_column: The column to filter on (e.g., Table.portfolio_id)
        
        Returns:
            Query: Filtered query with portfolio permission applied
        
        Examples:
            >>> from sqlalchemy.orm import Session
            >>> from backend.models import Position
            >>> session = Session()
            >>> query = session.query(Position)
            >>> filter = PermissionFilter()
            >>> filtered_query = filter.apply_portfolio_filter(
            ...     query, user_context, Position.portfolio_id
            ... )
        """
        # If user has no portfolio permissions, return empty result
        if not user_context.portfolio_ids:
            # Return query that will match nothing
            return query.filter(portfolio_id_column.in_([]))
        
        # Apply IN clause for portfolio IDs
        return query.filter(portfolio_id_column.in_(user_context.portfolio_ids))
    
    def apply_combined_filter(
        self,
        query: Query,
        user_context: UserContext,
        org_id_column: Column,
        portfolio_id_column: Optional[Column] = None
    ) -> Query:
        """
        Apply combined organization and portfolio permission filters.
        
        This method applies both organization and portfolio filters to a query.
        If portfolio_id_column is provided, it applies both filters.
        Otherwise, it only applies the organization filter.
        
        Args:
            query: SQLAlchemy Query object to filter
            user_context: User context containing permissions
            org_id_column: The organization ID column to filter on
            portfolio_id_column: Optional portfolio ID column to filter on
        
        Returns:
            Query: Filtered query with permissions applied
        
        Examples:
            >>> # Filter by organization only
            >>> filtered_query = filter.apply_combined_filter(
            ...     query, user_context, Trade.org_id
            ... )
            >>> 
            >>> # Filter by both organization and portfolio
            >>> filtered_query = filter.apply_combined_filter(
            ...     query, user_context, Trade.org_id, Trade.portfolio_id
            ... )
        """
        # Apply organization filter
        query = self.apply_org_filter(query, user_context, org_id_column)
        
        # Apply portfolio filter if column is provided
        if portfolio_id_column is not None:
            query = self.apply_portfolio_filter(
                query, user_context, portfolio_id_column
            )
        
        return query
    
    def build_org_filter_condition(
        self,
        user_context: UserContext,
        org_id_column: Column
    ) -> Any:
        """
        Build organization filter condition without applying to query.
        
        This method creates a filter condition that can be used in complex
        queries or combined with other conditions.
        
        Args:
            user_context: User context containing org_ids
            org_id_column: The column to filter on
        
        Returns:
            SQLAlchemy filter condition
        
        Examples:
            >>> condition = filter.build_org_filter_condition(
            ...     user_context, Trade.org_id
            ... )
            >>> query = session.query(Trade).filter(condition)
        """
        if not user_context.org_ids:
            # Return condition that matches nothing
            return org_id_column.in_([])
        
        return org_id_column.in_(user_context.org_ids)
    
    def build_portfolio_filter_condition(
        self,
        user_context: UserContext,
        portfolio_id_column: Column
    ) -> Any:
        """
        Build portfolio filter condition without applying to query.
        
        This method creates a filter condition that can be used in complex
        queries or combined with other conditions.
        
        Args:
            user_context: User context containing portfolio_ids
            portfolio_id_column: The column to filter on
        
        Returns:
            SQLAlchemy filter condition
        
        Examples:
            >>> condition = filter.build_portfolio_filter_condition(
            ...     user_context, Position.portfolio_id
            ... )
            >>> query = session.query(Position).filter(condition)
        """
        if not user_context.portfolio_ids:
            # Return condition that matches nothing
            return portfolio_id_column.in_([])
        
        return portfolio_id_column.in_(user_context.portfolio_ids)
    
    def has_org_access(
        self,
        user_context: UserContext,
        org_id: str
    ) -> bool:
        """
        Check if user has access to a specific organization.
        
        Args:
            user_context: User context containing org_ids
            org_id: Organization ID to check
        
        Returns:
            True if user has access, False otherwise
        """
        return org_id in user_context.org_ids
    
    def has_portfolio_access(
        self,
        user_context: UserContext,
        portfolio_id: str
    ) -> bool:
        """
        Check if user has access to a specific portfolio.
        
        Args:
            user_context: User context containing portfolio_ids
            portfolio_id: Portfolio ID to check
        
        Returns:
            True if user has access, False otherwise
        """
        return portfolio_id in user_context.portfolio_ids
    
    def filter_org_ids(
        self,
        user_context: UserContext,
        org_ids: List[str]
    ) -> List[str]:
        """
        Filter a list of organization IDs based on user permissions.
        
        Returns only the org_ids that the user has access to.
        
        Args:
            user_context: User context containing org_ids
            org_ids: List of organization IDs to filter
        
        Returns:
            List of organization IDs the user has access to
        
        Examples:
            >>> all_orgs = ['ORG001', 'ORG002', 'ORG003']
            >>> accessible_orgs = filter.filter_org_ids(user_context, all_orgs)
            >>> # Returns only orgs in user_context.org_ids
        """
        if not user_context.org_ids:
            return []
        
        user_org_set = set(user_context.org_ids)
        return [org_id for org_id in org_ids if org_id in user_org_set]
    
    def filter_portfolio_ids(
        self,
        user_context: UserContext,
        portfolio_ids: List[str]
    ) -> List[str]:
        """
        Filter a list of portfolio IDs based on user permissions.
        
        Returns only the portfolio_ids that the user has access to.
        
        Args:
            user_context: User context containing portfolio_ids
            portfolio_ids: List of portfolio IDs to filter
        
        Returns:
            List of portfolio IDs the user has access to
        
        Examples:
            >>> all_portfolios = ['PF001', 'PF002', 'PF003']
            >>> accessible = filter.filter_portfolio_ids(user_context, all_portfolios)
            >>> # Returns only portfolios in user_context.portfolio_ids
        """
        if not user_context.portfolio_ids:
            return []
        
        user_portfolio_set = set(user_context.portfolio_ids)
        return [pid for pid in portfolio_ids if pid in user_portfolio_set]
