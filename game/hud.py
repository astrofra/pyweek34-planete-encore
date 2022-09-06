import harfang as hg
from math import pi, cos, sin

# scroll text drawing routine
# on-screen usage text
def display_hud(dt, view_id, res_x, res_y, text, font, font_program, font_size, text_render_state, fade=1.0):
	
	# text_pos = hg.Vec3(0.0, 0.0, 0.0)
	r = hg.ComputeTextRect(font, text)
	text_pos = hg.Vec3((res_x - (r.ex - r.sx)) / 2, res_y - (font_size * 1.25), 0)

	bold_radius = (2.0 * res_x) / 1280
	# for l in range(0, int(bold_radius), 2):
	for a in range(0, 360, 30):
		bold_offset = hg.Vec3(cos(a * pi / 180.0), sin(a * pi / 180.0), 0.0) * bold_radius
		bold_offset.x = bold_offset.x
		bold_offset.y = bold_offset.y
		hg.DrawText(view_id, font, text, font_program, 'u_tex', 0, hg.Mat4.Identity, text_pos + bold_offset, 
		hg.DTHA_Left, hg.DTVA_Bottom, [hg.MakeUniformSetValue('u_color', hg.Vec4(0.1, 0.1, 0.1, fade))], [], text_render_state)
	
	hg.DrawText(view_id, font, text, font_program, 'u_tex', 0, hg.Mat4.Identity, text_pos, hg.DTHA_Left, hg.DTVA_Bottom, [hg.MakeUniformSetValue('u_color', hg.Vec4(1, 1, 1, fade))], [], text_render_state)

	return view_id
# end