![Preview screenshot](https://raw.githubusercontent.com/whizikxd/blender-export-as-array/master/assets/screenshot.png)

Small addon to export a mesh to a programming language array

### Example output
```py
verts = [
	[ 1.0, 1.0, 1.0 ],
	[ 1.0, 1.0, -1.0 ],
	[ 1.0, -1.0, 1.0 ],
	[ 1.0, -1.0, -1.0 ],
	[ -1.0, 1.0, 1.0 ],
	[ -1.0, 1.0, -1.0 ],
	[ -1.0, -1.0, 1.0 ],
	[ -1.0, -1.0, -1.0 ]
]

faces = [
	[ 0, 4, 6, 2 ],
	[ 3, 2, 6, 7 ],
	[ 7, 6, 4, 5 ],
	[ 5, 1, 3, 7 ],
	[ 1, 0, 2, 3 ],
	[ 5, 4, 0, 1 ]
]
```