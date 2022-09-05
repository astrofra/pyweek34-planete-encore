# PyWeek 34 -- September 2022
# P L A N E T E   E N C O R E

import harfang as hg
from utils import *
from config_gui import *
from hud import display_hud
from math import pi, sin

def draw_line(pos_a, pos_b, line_color, vid, vtx_line_layout, line_shader):
	vtx = hg.Vertices(vtx_line_layout, 2)
	vtx.Begin(0).SetPos(pos_a).SetColor0(line_color).End()
	vtx.Begin(1).SetPos(pos_b).SetColor0(line_color).End()
	hg.DrawLines(vid, vtx, line_shader)


def main():
	# {}
	config = {"enable_aaa":True, "low_aaa":False, "skip_intro":False}

	# hg.SetLogLevel(hg.LL_Normal)

	hg.InputInit()
	hg.AudioInit()
	hg.WindowSystemInit()

	hg.AddAssetsFolder("assets_compiled")

	hg.ShowCursor()
	config_done, default_res_x, default_res_y, default_fullscreen, full_aaa, low_aaa, no_aaa = config_gui()

	# set config
	res_x, res_y = default_res_x, default_res_y

	if no_aaa:
		config["enable_aaa"] = False 
	else:
		config["enable_aaa"] = True
		if low_aaa:
			config["low_aaa"] = True
		else:
			config["low_aaa"] = False
		# end
	# end

	if config_done == 1: 
		# Demo start
		# res_x, res_y = resolution_multiplier(res_x, res_x, 0.8)
		res_vec2 = hg.Vec2(res_x, res_y)
		font_size = int((60 * res_x) / 1280)

		# win = hg.RenderInit('Minisub Escape', res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)
		win = hg.NewWindow("Planete Encore", res_x, res_y, 32, default_fullscreen) #, hg.WV_Fullscreen)
		hg.RenderInit(win)
		hg.RenderReset(res_x, res_y, hg.RF_MSAA4X | hg.RF_MaxAnisotropy)

		# create pipeline
		pipeline = hg.CreateForwardPipeline()
		res = hg.PipelineResources()

		# INTRO
		scene = hg.Scene()
		hg.LoadSceneFromAssets("main.scn", scene, res, hg.GetForwardPipelineInfo())

		cam_game = scene.GetNode("Camera")
		scene.SetCurrentCamera(cam_game)

		# physics
		physics = hg.SceneBullet3Physics()
		physics.SceneCreatePhysicsFromAssets(scene)

		scene_clocks = hg.SceneClocks()

		# # create a plane model for the dirt particles
		# vtx_layout = hg.VertexLayoutPosFloatNormUInt8TexCoord0UInt8()

		# particle_intro_mdl = build_random_particles_model(hg.ModelBuilder(), vtx_layout, 3, 25.0)

		# # particle_dirt_mdl = hg.CreatePlaneModel(vtx_layout, 1, 1, 1, 1) # generic quad
		# particle_dirt_mdl = build_random_particles_model(hg.ModelBuilder(), vtx_layout, 5, 15.0)

		# particle_dirt_ref = res.AddModel('dirt_particle', particle_dirt_mdl)
		# particle_dirt_render_state = hg.ComputeRenderState(hg.BM_Alpha, hg.DT_Less, hg.FC_Disabled, False)

		# shader to draw some 3D lines
		vtx_line_layout = hg.VertexLayoutPosFloatColorUInt8()
		shader_for_line = hg.LoadProgramFromAssets("shaders/pos_rgb")
		shader_for_particle = hg.LoadProgramFromAssets("shaders/dirt_particle")
		dirt_particle_texture,_ = hg.LoadTextureFromAssets("maps/dirt_particle.png", 
										hg.TF_UBorder | hg.TF_VBorder | hg.TF_SamplerMinAnisotropic | hg.TF_SamplerMagAnisotropic)

		# text rendering
		# load font and shader program
		font = hg.LoadFontFromAssets('fonts/zector.ttf', font_size)
		font_program  = hg.LoadProgramFromAssets('core/shader/font')

		# text uniforms and render state
		text_uniform_values = [hg.MakeUniformSetValue('u_color', hg.Vec4(1, 1, 0, 1))]
		text_render_state = hg.ComputeRenderState(hg.BM_Alpha, hg.DT_Always, hg.FC_Disabled)

		# Set render camera
		cam = scene.GetNode("Camera")
		scene.SetCurrentCamera(cam)
		z_near = cam.GetCamera().GetZNear()
		z_far = cam.GetCamera().GetZFar()
		fov = cam.GetCamera().GetFov()

		# mouse
		# mouse = hg.Mouse()
		keyboard = hg.Keyboard('raw')

		hg.HideCursor()

		# Demo AAA pipeline config
		# pipeline_aaa_config, pipeline_aaa
		if config["enable_aaa"]:
			pipeline_aaa_config = hg.ForwardPipelineAAAConfig()
			pipeline_aaa = hg.CreateForwardPipelineAAAFromAssets("core", pipeline_aaa_config, hg.BR_Half, hg.BR_Half)
			if config["low_aaa"]:
				pipeline_aaa_config.temporal_aa_weight = 0.2
				pipeline_aaa_config.sample_count = 1
			else:
				pipeline_aaa_config.temporal_aa_weight = 0.05
				pipeline_aaa_config.sample_count = 2
			# end
			pipeline_aaa_config.z_thickness = 1.0 # in meters
			pipeline_aaa_config.bloom_bias = 0.00999
			pipeline_aaa_config.bloom_intensity	= 1.0
			pipeline_aaa_config.bloom_threshold	= 4.25 * 3.0
		# end

		# Demo loop ###################################################
		frame = 0

		smila = {"node": scene.GetNode("smila"), "trs": None, "pos": None, "rot": None}
		smila["trs"] = smila["node"].GetTransform()
		smila["pos"] = smila["trs"].GetPos()
		smila["rot"] = smila["trs"].GetRot()
		rotation_speed = hg.DegreeToRadian(10.0)
		walk_speed = 1.5
		run_speed = walk_speed * 2.5

		smila["anims"] = {}
		for anim_name in ["idle", "walk", "run", "die"]:
			smila["anims"][anim_name] = smila["node"].GetInstanceSceneAnim(anim_name)
		# scene.PlayAnim(smila["anims"]["die"], hg.ALM_Loop)

		current_anim_mode = "idle"
		current_anim_ref = None
		prev_anim_mode = None

		while not hg.ReadKeyboard().Key(hg.K_Escape) & hg.IsWindowOpen(win):
			keyboard.Update()
			
			lines = []
			lines.append({"pos_a": hg.Vec3(0,-10,0), "pos_b": hg.Vec3(0,10,0), "color": hg.Color.White})
			dt = min(hg.time_from_sec_f(5.0/60.0), hg.TickClock())
			dts = hg.time_to_sec_f(dt)
			# clock = clock + dt

			# hero control
			if current_anim_mode != prev_anim_mode:
				if current_anim_ref is not None:
					scene.StopAnim(current_anim_ref)
				current_anim_ref = scene.PlayAnim(smila["anims"][current_anim_mode], hg.ALM_Loop)
				prev_anim_mode = current_anim_mode

			if keyboard.Down(hg.K_Left):
				smila["rot"].y += dts * rotation_speed * 20.0
			elif keyboard.Down(hg.K_Right):
				smila["rot"].y -= dts * rotation_speed * 20.0

			forward = hg.GetColumn(smila["trs"].GetWorld(), 0)
			forward = hg.Vec3(forward.x, forward.y, forward.z)
			forward = hg.Normalize(forward)
			lines.append({"pos_a": smila["pos"] + hg.Vec3(0,1,0), "pos_b": smila["pos"] + forward * 5.0 + hg.Vec3(0,1,0), "color": hg.Color.Red})

			if keyboard.Down(hg.K_Up):
				if keyboard.Down(hg.K_LShift):
					smila["pos"] += forward * dts * run_speed
					current_anim_mode = "run"					
				else:
					smila["pos"] += forward * dts * walk_speed
					current_anim_mode = "walk"
			else:
				current_anim_mode = "idle"
			
			smila["trs"].SetPos(smila["pos"])
			smila["trs"].SetRot(smila["rot"])

			hg.SceneUpdateSystems(scene, scene_clocks, dt, physics, hg.time_from_sec_f(1 / 60), 4)
			physics.SyncTransformsToScene(scene)
			# scene.Update(dt)

			# main framebuffer
			view_id = 0
			if config["enable_aaa"]:
				view_id, pass_ids = hg.SubmitSceneToPipeline(view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res, pipeline_aaa, pipeline_aaa_config, frame)
			else:
				view_id, pass_ids = hg.SubmitSceneToPipeline(view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res)
			# end

			# debug draw lines
			opaque_view_id = hg.GetSceneForwardPipelinePassViewId(pass_ids, hg.SFPP_Opaque)
			for i in range(len(lines)):
				draw_line(lines[i]["pos_a"], lines[i]["pos_b"], lines[i]["color"], opaque_view_id, vtx_line_layout, shader_for_line)
			# end

			view_id = view_id + 1
			hg.SetView2D(view_id, 0, 0, res_x, res_y, -1, 1, hg.CF_None, hg.Color.Black, 1, 0)

			# view_id, scroll_x, char_offset, ns = update_demo_scroll_text(dt, view_id, res_x, res_y, scroll_x, char_offset, ns, scroll_text, font, font_program, font_size, text_render_state, EaseInOutQuick(fade))
			view_id = display_hud(dt, view_id, res_x, res_y, "Score : 12300", font, font_program, font_size, text_render_state, 1.0)

			# Debug physics display
			if False:
				view_id = view_id + 1
				hg.SetViewClear(view_id, 0, 0, 1.0, 0)
				hg.SetViewRect(view_id, 0, 0, res_x, res_y)
				cam_mat = cam.GetTransform().GetWorld()
				view_matrix = hg.InverseFast(cam_mat)
				c = cam.GetCamera()
				projection_matrix = hg.ComputePerspectiveProjectionMatrix(c.GetZNear(), c.GetZFar(), hg.FovToZoomFactor(c.GetFov()), hg.Vec2(res_x / res_y, 1))
				hg.SetViewTransform(view_id, view_matrix, projection_matrix)
				rs = hg.ComputeRenderState(hg.BM_Opaque, hg.DT_Disabled, hg.FC_Disabled)
				physics.RenderCollision(view_id, vtx_line_layout, shader_for_line, rs, 0)

			frame = hg.Frame()
			hg.UpdateWindow(win)

		hg.RenderShutdown()
		hg.WindowSystemShutdown()
	# end
# end

main()

