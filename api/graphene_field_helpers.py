import graphql
from collections import abc
from typing import Union

def selected_field_names(selection_set: graphql.SelectionSetNode,
                         info: graphql.GraphQLResolveInfo,
                         runtime_type: Union[str, graphql.GraphQLObjectType] = None) -> abc.Iterator[str]:
    """ Get the list of field names that are selected at the current level. Does not include nested names.

    This function re-evaluates the AST, but gives a complete list of included fields.
    It is 25x slower than `selected_field_names_naive()`, but still, it completes in 7ns or so. Not bad.

    Args:
        selection_set: the selected fields
        info: GraphQL resolve info
        runtime_type: The type of the object you resolve to. Either its string name, or its ObjectType.
            If none is provided, this function will fail with a RuntimeError() when resolving fragments
    """
    # Create a temporary execution context. This operation is quite cheap, actually.
    execution_context = graphql.ExecutionContext(
        schema=info.schema,
        fragments=info.fragments,
        root_value=info.root_value,
        operation=info.operation,
        variable_values=info.variable_values,
        # The only purpose of this context is to be able to run the collect_fields() method.
        # Therefore, many parameters are actually irrelevant
        context_value=None,
        field_resolver=None,
        type_resolver=None,
        errors=[],
        middleware_manager=None,
    )

    # Use it
    return selected_field_names_from_context(selection_set, execution_context, runtime_type)


def selected_field_names_from_context(
        selection_set: graphql.SelectionSetNode,
        context: graphql.ExecutionContext,
        runtime_type: Union[str, graphql.GraphQLObjectType] = None) -> abc.Iterator[str]:
    """ Get the list of field names that are selected at the current level.

    This function is useless because `graphql.ExecutionContext` is not available at all inside resolvers.
    Therefore, `selected_field_names()` wraps it and provides one.
    """
    assert isinstance(selection_set, graphql.SelectionSetNode)

    # Resolve `runtime_type`
    if isinstance(runtime_type, str):
        runtime_type = context.schema.type_map[runtime_type]  # raises: KeyError

    # Resolve all fields
    fields_map = context.collect_fields(
        # Use the provided Object type, or use a dummy object that fails all tests
        runtime_type=runtime_type or None,
        # runtime_type=runtime_type or graphql.GraphQLObjectType('<temp>', []),
        selection_set=selection_set,
        fields={},  # out
        visited_fragment_names=(visited_fragment_names := set()),  # out
    )

    # Test fragment resolution
    if visited_fragment_names and not runtime_type:
        raise RuntimeError('The query contains fragments which cannot be resolved '
                           'because `runtime_type` is not provided by the lazy developer')

    # Results!
    return (
        field.name.value
        for fields_list in fields_map.values()
        for field in fields_list
    )


def get_requested_fields(info):
    return selected_field_names(info.field_nodes[0].selection_set)
