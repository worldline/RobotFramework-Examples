from robot.running.model import TestSuite
from robot.libraries.BuiltIn import BuiltIn
from robot.running.context import EXECUTION_CONTEXTS
from robot.api import logger
from robot.api.deco import library, keyword
from robot.errors import VariableError
from RoboPandas import create_dataframe
import random

@library(scope='TEST SUITE', doc_format='reST')
class Examples(object):
    """Examples library adds support of a list of Example test data to Robot Framewok test cases.

    With Examples, a Data driven test case can be defined where the data and the test process
    are kept together in the same part of the test case definition file, eliminating a
    cognitive split between these parts of a test scenario definition.

    Unlike template test cases, multiple similar scenarios can be present in the same robot file.

    To use the Examples: keyword, this library must be referenced in the test suite. 
    As long as autoexpand is not set to false, Expand Test Examples (below) is automatically called.
    An example of a test case defined with Examples:

    .. code:: robotframework
        
        *** Settings ***
        Library    Examples
        
        *** Test cases ***
        My test with examples for ${name}
            Log    Hello ${name}, welcome to ${where welcome}    console=True
            Examples:    name      where welcome    --
                    ...    Joe       the world!
                    ...    Arthur    Camelot (clip clop).
                    ...    Patsy     it's only a model!

    After expansion, this is equivalent to:

    .. code:: robotframework

        *** Test cases ***
        My test with examples for Joe
            Log    Hello Joe, welcome to the world!    console=True

        My test with examples for Arthur
            Log    Hello Arthur, welcome to Camelot (clip clop).    console=True
            
        My test with examples for Patsy
            Log    Hello Patsy, welcome to it's only a model    console=True
    """

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, autoexpand=True, max_examples=None, random=None):
        """max_example and random can be specified globally as described above.

        These arguments can be over-ridden for individual calls to Expand Test Examples.

        In certain scenario's, data may be retrieved from external sources or defined by other keywords.
        When this is needed, Library Examples should have autoexpand=False.
        In this case, the variables needed for the example data to be resolved can be defined first during
        Suite setup, then Expand test examples can be explicitly called once the data is ready.
        """

        self.ROBOT_LIBRARY_LISTENER = self
        self.current_suite = None
        self.autoexpand = False if hasattr(autoexpand, 'lower') and autoexpand.lower() in ['false', 'no', 'off', 'f', '0'] else autoexpand
        self.max_examples = int(max_examples) if max_examples else max_examples
        self.random = random

    def _start_suite(self, suite, result):
        # save current suite so that we can modify it later
        self.current_suite = suite
        if self.autoexpand:
            self.expand_test_examples()

    def _localise_scope(self):
        # Create a local scope for providing keyword arguments to user
        # specified keywords.
        variables = EXECUTION_CONTEXTS.current.variables
        outside_scope = variables.current
        variables.start_keyword()

        # Copy the outside scope to the internal scope.
        # This is done because one would expect the variables from the current scope of this keyword to be available.
        # Therefore, local script variables can also be referred to in the
        # spreadsheet.
        variables.current.update(outside_scope)

        return variables

    @keyword()
    def examples(self, *examples_data):
        """This keyword is not called. This keyword is searched for and removed by Expand test examples.

        The arguments are expanded to create concrete test cases as described by Expand Test Examples."""
        BuiltIn().fail('Expand Test Examples should be called in Suite setup.')

    @keyword()
    def expand_test_examples(self, max_examples=None, random=None):
        """The "Examples:" keyword is searched for in test cases by this keyword, Either automatically
        by the library import, or explicitly when autoexpand is False. 
        When Examples: is found, the following occurs:

        * Column headers are determined as the first arguments before the '--' delimiter argument
        * Data rows are combined with the headers to form a dataframe.
        * The number of data arguments MUST be an exact multiple of the number of headers.
        * A new test case is created for each row in the table of examples.
        * If max_examples is specified, no more than max_examples test cases are produced for this scenario.
        * When random is specified, the examples are chosen in a random order. 
          If this is a number, it is also used as max_examples.
        * The new test case is search for variables where the variable name matches a coloumn header name.
          When a matching variable name is found, it is replaced with the example value.
        * Any variables in scope at the time of example replacement (e.g. global variables) are replaced as
          actual values in the test.
        * Test case name is searched and replaced. This is necessary for Robot Framework to have unique test
          names.
        * Keyword names, argument values, Tags, IF conditions and FOR loops arguments are replaced 
          with variable values in scope at the time of replacement.

        Optional argument random can be used to specify that examples should be in a random order.
        When random is an integer and max_examples is not specified, it will be used as the number of examples to choose.

        Argument max_examples can be used to specify the maximum number of examples to process.

        This can be helpful if the examples are dynamically defined using generated arguments and for
        development purposes."""
        self._max_examples = int(max_examples) if max_examples else self.max_examples
        self._random = random if random else self.random
        if self._random and not max_examples:
            try:
                self._max_examples = int(self._random)
            except ValueError:
                pass
        self._expand_tcs_in_suite(self.current_suite)

    def _expand_tcs_in_suite(self, suite):
        replacement_tests = []
        for tc in suite.tests:
            if not self._expand_example_tc(tc):
                replacement_tests.append(tc)
        self.current_suite.tests = replacement_tests
        for suite in suite.suites:
            self._expand_tcs_in_suite(suite)

    def _expand_example_tc(self, example_tc):
        for kw in example_tc.body:
            try:
                if kw.name.lower() == 'examples:':
                    args = BuiltIn()._variables.replace_list(kw.args)
                    break
            except AttributeError:
                continue
        else:
            return False
        records = create_dataframe(*args).to_dict('records')
        if self._random:
            example_data = random.sample(records, self._max_examples or len(records))
        else:
            example_data = records[0:self._max_examples]

        self.variables = self._localise_scope()
        for example in example_data:
            self.variables.current.store.data.update(example)
            filled_tc = self.current_suite.tests.create(self.variables.replace_scalar(example_tc.name, ignore_errors=True))
            filled_tc.setup = example_tc.setup
            filled_tc.teardown = example_tc.teardown
            filled_tc.tags = self.replace_list(example_tc.tags)
            self._populate_example_to_body(example_tc.body, filled_tc.body)

        self.variables.end_keyword()
        return True

    def _populate_example_to_body(self, body, target):
        for kw in body:
            if kw.type == 'KEYWORD':
                if kw.name.lower() == 'examples:':
                    continue
                target.create_keyword(self.variables.replace_scalar(kw.name, ignore_errors=True), 
                        args = self.replace_list(kw.args),
                        assign=self.replace_list(kw.assign),
                        tags=self.replace_list(kw.tags),
                        timeout=kw.timeout,
                        lineno=kw.lineno)
            else:
                new_kw = kw.deepcopy()
                new_kw.body = None
                if hasattr(new_kw, 'values'):
                    new_kw.values = self.replace_list(kw.values)
                if hasattr(new_kw, 'condition'):
                    new_kw.condition = self.ariables.replace_scalar(kw.condition, ignore_errors=True)
                    # TODO: replacement for IF is also necessary - I currently don't have an example of this use-case to test
                self._populate_example_to_body(kw.body, new_kw.body)
                target.append(new_kw)

    def replace_list(self, args):
        try:
            return self.variables.replace_list(args)
        except VariableError as e:
            result = self.variables.replace_list(args, ignore_errors=True)
            logger.info(f'{e}.\nCurrent result is {result}')
            return result
