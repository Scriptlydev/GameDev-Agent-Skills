extends RefCounted

var ready := false

func before_each():
	ready = true

func after_each():
	ready = false

func test_first():
	if not ready:
		return "before_each did not run"
	return null

func test_second():
	return null

func test_requires_argument(value):
	return value
