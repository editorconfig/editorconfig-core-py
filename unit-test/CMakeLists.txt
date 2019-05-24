#
# Build unit-tests
#

enable_testing()

function(glob_test glob regex)
    string(REPLACE " " "_" test_name "Glob2Re_${glob}")

    # Is a test with this name already defined?
    get_test_property(${test_name} LABELS labels)
    if(NOT "${labels}" STREQUAL "NOTFOUND")
        message(SEND_ERROR "Duplicate test: ${test_name}")
    endif()

    add_test(${test_name} ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/create_re_utest.py
        "${glob}" "${regex}")
    set_tests_properties(${test_name} PROPERTIES "LABELS" "unit-test-glob")

endfunction()

# First test if the test command would really fail.
glob_test("ShouldFail-*.c" "^ShouldFail$")
set_tests_properties("Glob2Re_ShouldFail-*.c" PROPERTIES WILL_FAIL TRUE)

# basics
glob_test("*.c" "^[^/]*\\\\.c$")
glob_test("a b.c" "^a\\\\ b\\\\.c$")
glob_test("test/**/b.c" "^test(?:/|/.*/)b\\\\.c$")
glob_test("test/*/b.c" "^test/[^/]*/b\\\\.c$")
glob_test("**/b.c" "^.*/b\\\\.c$")

# brackets
glob_test("[abc]" "^[abc]$")
glob_test("[a-z]" "^[a-z]$")

# support ^ and ! as negation
glob_test("[!abc]" "^[^abc]$")
glob_test("[^abc]" "^[^abc]$")

glob_test("[abc[]" "^[abc[]$")
glob_test("[abc\\\\[]" "^[abc[]$")
glob_test("[abc\\\\]]" "^[abc\\\\]]$")
glob_test("[abc\\\\[\\\\]]" "^[abc[\\\\]]$")
glob_test("[abc[\\\\]]" "^[abc[\\\\]]$")

glob_test("[test[abc]" "^[test[abc]$")
glob_test("[test\\\\[abc]" "^[test[abc]$")
glob_test("[test\\\\]abc]" "^[test\\\\]abc]$")
glob_test("[test]abc]" "^[test]abc\\\\]$")
glob_test("[test" "^\\\\[test$")
glob_test("]test" "^\\\\]test$")

# choice
glob_test("{}" "^\\\\{\\\\}$")
glob_test("{test}" "^\\\\{test\\\\}$")
glob_test("{test,case}" "^(?:test|case)$")
glob_test("{test,case,}" "^(?:test|case|)$")
glob_test("{test,case,[!abc]}" "^(?:test|case|[^abc])$")

# comma inside brackets is choice separator
glob_test("{test[a,b]case,2}" "^(?:test\\\\[a|b\\\\]case|2)$")
glob_test("{test[a\\\\,b]case,2}" "^(?:test[a,b]case|2)$")

# choice in choice
glob_test("test.{a-{first,second},b-{third,fourth}}"
    "^test\\\\.(?:a\\\\-(?:first|second)|b\\\\-(?:third|fourth))$")

# incomplete outer braces
glob_test("{test{test,case}" "^\\\\{test(?:test|case)$")
glob_test("test{test,case}}" "^test(?:test|case)\\\\}$")

# back to back braces
glob_test("}test{" "^\\\\}test\\\\{$")

# simple number ranges
glob_test("{0..9}" "^(?:[0-9])$")
glob_test("{1..5}" "^(?:[1-5])$")
glob_test("{+1..5}" "^(?:[1-5])$")
glob_test("{1..+5}" "^(?:[1-5])$")
glob_test("{+1..+5}" "^(?:[1-5])$")
glob_test("{5..1}" "^(?:[1-5])$")
glob_test("{0..5}" "^(?:[0-5])$")
glob_test("{0..15}" "^(?:[0-9]|1[0-5])$")
glob_test("{9..15}" "^(?:9|1[0-5])$")
glob_test("{10..15}" "^(?:1[0-5])$")
glob_test("{11..15}" "^(?:1[1-5])$")
glob_test("{11..20}" "^(?:1[1-9]|20)$")
glob_test("{11..23}" "^(?:1[1-9]|2[0-3])$")
glob_test("{11..32}" "^(?:1[1-9]|2[0-9]|3[0-2])$")
glob_test("{11..39}" "^(?:1[1-9]|[2-3][0-9])$")
glob_test("{1..39}" "^(?:[1-9]|[1-3][0-9])$")
glob_test("{0..39}" "^(?:[0-9]|[1-3][0-9])$")
glob_test("{0..999}"
    "^(?:[0-9]|[1-9][0-9]|[1-9][0-9][0-9])$")
glob_test("{0..9999}"
    "^(?:[0-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9])$")
glob_test("{0..99999}"
    "^(?:[0-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]|[1-9][0-9][0-9][0-9][0-9])$")

glob_test("{-1..-5}" "^(?:\\\\-(?:[1-5]))$")
glob_test("{-5..-1}" "^(?:\\\\-(?:[1-5]))$")
glob_test("{0..-5}" "^(?:\\\\-(?:[1-5])|0)$")
glob_test("{-0..-5}" "^(?:\\\\-(?:[1-5])|0)$")
glob_test("{+0..-5}" "^(?:\\\\-(?:[1-5])|0)$")

glob_test("{-3..5}" "^(?:\\\\-(?:[1-3])|[0-5])$")

# justified number ranges
glob_test("{00..15}" "^(?:0[0-9]|1[0-5])$")
glob_test("{15..00}" "^(?:0[0-9]|1[0-5])$")
glob_test("{01..39}" "^(?:0[1-9]|[1-3][0-9])$")
glob_test("{00..39}" "^(?:0[0-9]|[1-3][0-9])$")
glob_test("{00..999}"
    "^(?:[0-9][0-9][0-9])$")
glob_test("{0..0999}"
    "^(?:0[0-9][0-9][0-9])$")
glob_test("{00..-999}"
    "^(?:\\\\-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9][0-9])|0000)$")
glob_test("{-00..9999}"
    "^(?:[0-9][0-9][0-9][0-9])$")
glob_test("{0..-09999}"
    "^(?:\\\\-(?:0000[1-9]|000[1-9][0-9]|00[1-9][0-9][0-9]|0[1-9][0-9][0-9][0-9])|000000)$")

glob_test("{-03..5}" "^(?:\\\\-(?:0[1-3])|00[0-5])$")


