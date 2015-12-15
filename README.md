# safeserver #
This is a proof-of-concept implementation for record-keeping strings.  It demonstrates how this string class could be used to prevent injection into SQL queries, even with an incompetent developer constructing these queries.  This is accomplished by marking input strings as dangerous when they are recieved, and then inspecting the dangerous portions of the string before the SQL query is run.

This repo contains three modules of note, plus an example implementation of a web server that uses them.  A live version of this site is available at http://injection-free-server.appspot.com/.  Although the SQL query is constructed in a very unsafe way, it properly rejects injection attempts.

## safeserver.py ##
This module provides the API for constructing the server.  The API is exactly the same as (and uses) the webapp2 module, which means it can be used to write applications on Google App Engine.  The only difference with webapp2 is that safeserver marks user input as dangerous.

## safesql.py ##
This module provides the API for making SQL queries, which is the same as (and uses) the MySQLdb module.  The addition is that, if it detects injection, it throws an InjectionError exception.

Injection is detected with the following steps:

1. Parse the attempted query into tokens
2. Extract the dangerous parts (those that came from the user)
3. For each, find the token that corresponds to this part.
4. If for any part, there is no corresponding token, reject the query.
5. Otherwise, the query is safe and can be run.

The requirement that dangerous strings correspond to a token is nearly the same as that in the definition of injection, but it is not *quite* the same.  It is possible that it could generate a few false positives, though it will still work for the common cases of SQL vulnerabilities.  This compromise was made due to the nature of the sqlparse module.  A true abstract syntax tree builder would be better.

## safestring.py ##
This module does the work of keeping track of dangerous parts of strings.  It supports nearly all of the same methods as the built-in string class, so writers of the server can use it without the knowledge that it is not the built-in string.

SafeString objects, like strings, are immutable.  Each is represented as a tree of strings, some of which are marked unsafe.  An in-order traversal of the tree provides the true representation of the string.  The tree structure is used because it makes it easier to keep SafeStrings immutable and to reuse chunks for memory efficiency.

## main.py ##
This is the implementation of the web server using this framework.  It was built using Google's own tutorial, but replacing their import statements with imports for this module.

### Vulnerabilities ###

This server has two injection vulnerabilities.  The first is on line 60, where the database is searched, and the second on line 94, where data is inserted.  Both are the result of string concatenation, and both will be caught and rejected.

# Improvements #
This implementation of SafeStrings is not optimized.  The best optimization would be to properly balance the trees, however some operations could also be sped up (they were written for clarity and functionality).  It is assumed that most strings are not made of too many concatenated substrings, so these operations should still be fine for most purposes.

As this is a proof of concept, functionality is the most important thing.  Were this feature to make its way into an actual language, design considerations would have to be made, and performance would matter.  However, this set of modules shows that record-keeping strings are feasible and can prevent real injection vulnerabilities.
