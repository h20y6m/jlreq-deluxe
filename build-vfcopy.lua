
local vfcopy_jlreq_list = {"ml","mr","mb","gr","gb","ge","mgr"}

local function jfmutil_vfcopy_1(in_vf,out_vf,out_base_tfm)
  print(">jfmutil vfcopy " .. in_vf .. " " .. out_vf .. " " .. out_base_tfm)
  run(
    ".",
    "jfmutil vfcopy " .. in_vf .. " " .. out_vf .. " " .. out_base_tfm
  )
end

local function jfmutil_vfcopy_2(in_vf,out_vf,out_base_tfm_1,out_base_tfm_2)
  print(">jfmutil vfcopy " .. in_vf .. " " .. out_vf .. " " .. out_base_tfm_1 .. " " .. out_base_tfm_2)
  run(
    ".",
    "jfmutil vfcopy " .. in_vf .. " " .. out_vf .. " " .. out_base_tfm_1 .. " " .. out_base_tfm_2
  )
end

local function vfcopy_jlreq()
  local prefix_list = {"","b","z","bz"}
  for _,s in pairs(vfcopy_jlreq_list) do
    -- for pTeX yoko
    for _,p in pairs(prefix_list) do
      -- jfmutil vfcopy [b][z]jlreq [b][z]jldx(ml|mr|...)-h r-jldx(ml|mr|...)-h
      jfmutil_vfcopy_1(p .. "jlreq", p .. "jldx" .. s .. "-h", "r-jldx" .. s .. "-h")
    end
    -- for pTeX tate
    for _,p in pairs(prefix_list) do
      -- jfmutil vfcopy [b][z]jlreq-v [b][z]jldx(ml|mr|...)-v r-jldx(ml|mr|...)-v
      jfmutil_vfcopy_1(p .. "jlreq-v", p .. "jldx" .. s .. "-v", "r-jldx" .. s .. "-v")
    end
    -- for upTeX yoko
    for _,p in pairs(prefix_list) do
      -- jfmutil vfcopy u[b][z]jlreq u[b][z]jldx(ml|mr|...)-h r-jldx(ml|mr|...)-h u[b][z]jldx(ml|mr|...)-hq
      jfmutil_vfcopy_2("u" .. p .. "jlreq", "u" .. p .. "jldx" .. s .. "-h", "r-ujldx" .. s .. "-h", "u" .. p .. "jldx" .. s .. "-hq")
      -- jfmutil vfcopy u[b][z]jlreq-q u[b][z]jldx(ml|mr|...)-hq r-jldx(ml|mr|...)-hq
      jfmutil_vfcopy_1("u" .. p .. "jlreq-q", "u" .. p .. "jldx" .. s .. "-hq", "r-ujldx" .. s .. "-hq")
    end
    -- for upTeX tate
    for _,p in pairs(prefix_list) do
      -- jfmutil vfcopy u[b][z]jlreq-v u[b][z]jldx(ml|mr|...)-v r-jldx(ml|mr|...)-v
      jfmutil_vfcopy_1("u" .. p .. "jlreq-v", "u" .. p .. "jldx" .. s .. "-v", "r-ujldx" .. s .. "-v")
    end
  end
  return 0
end

function vfcopy()
  vfcopy_jlreq()
end
