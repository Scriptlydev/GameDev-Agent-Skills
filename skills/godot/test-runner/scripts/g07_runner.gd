# Runs only inside the disposable project. Markers and engine errors use stderr.
extends SceneTree

const MARK := "G07_TEST_RUNNER"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		quit(2)
		return
	var config = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not config is Dictionary:
		quit(2)
		return
	for path in config["files"]:
		_run_file(path, config["filter"])
	printerr(MARK + " DONE")
	quit(0)


func _run_file(path: String, selection: String) -> void:
	var script = load(path)
	if not script is GDScript or not script.can_instantiate() or script.get_instance_base_type() not in ["RefCounted", "Object"]:
		printerr(MARK + " LOAD_ERROR " + JSON.stringify(path))
		return
	var methods: Array[String] = []
	for method in script.get_script_method_list():
		var name: String = method["name"]
		if name.begins_with("test_") and method["args"].is_empty():
			methods.append(name)
	methods.sort()
	for method in methods:
		var id := path + "::" + method
		if not selection.is_empty() and not id.contains(selection):
			continue
		printerr(MARK + " START " + JSON.stringify(id))
		# A separate call lets the loop continue when a test aborts on runtime error.
		_run_test(script, method, id)


func _run_test(script: GDScript, method: String, id: String) -> void:
	var started := Time.get_ticks_usec()
	var instance = script.new()
	if instance == null:
		printerr(MARK + " LOAD_ERROR " + JSON.stringify(id.get_slice("::", 0)))
		return
	if instance.has_method("before_each"):
		instance.call("before_each")
	var value = instance.call(method)
	if instance.has_method("after_each"):
		instance.call("after_each")
	var result := "pass"
	var message := ""
	if value is String:
		message = value
		result = "skipped" if value.begins_with("SKIP:") else "fail"
	elif value != null:
		result = "fail"
		message = "non-string return"
	if not instance is RefCounted:
		instance.free()
	printerr(MARK + " END " + JSON.stringify({"id": id, "result": result,
		"message": message, "duration_ms": (Time.get_ticks_usec() - started) / 1000.0}))
