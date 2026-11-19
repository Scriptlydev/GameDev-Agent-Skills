# G01 scene-doctor native load check. Copied into a DISPOSABLE workspace copy only.
# Loads each listed resource without instantiating scenes (no _ready/_init on nodes).
# Markers go to stderr so they interleave with Godot's own error output in order.
extends SceneTree

const MARK := "G01_SCENE_DOCTOR"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.is_empty():
		printerr(MARK + " ERROR no scene list")
		quit(2)
		return
	var list := FileAccess.open(args[0], FileAccess.READ)
	if list == null:
		printerr(MARK + " ERROR cannot open scene list")
		quit(2)
		return
	while not list.eof_reached():
		var path := list.get_line().strip_edges()
		if path.is_empty():
			continue
		printerr(MARK + " BEGIN " + path)
		var result := {"path": path, "exists": ResourceLoader.exists(path), "loaded": false, "type": "", "nodes": -1}
		var res := ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE)
		if res != null:
			result["loaded"] = true
			result["type"] = res.get_class()
			if res is PackedScene:
				result["nodes"] = (res as PackedScene).get_state().get_node_count()
		printerr(MARK + " RESULT " + JSON.stringify(result))
	printerr(MARK + " DONE")
	quit(0)
