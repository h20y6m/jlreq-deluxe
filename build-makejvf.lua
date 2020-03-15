
local function jfmutil_jodel(in_vf,prefix)
  print(">jfmutil jodel " .. in_vf .. " " .. prefix)
  run(
    ".",
    "jfmutil jodel " .. in_vf .. " " .. prefix
  )
end

local function jfmutil_jodel_jlreq()
  local jlreq_prefix_list = {"","b","z","bz"}
  for _,p in pairs(jlreq_prefix_list) do
    -- for pTeX yoko
    -- jfmutil jodel [b][z]jlreq [b][z]jlreq
    jfmutil_jodel(p .. "jlreq", p .. "jlreq")
    -- for pTeX tate
    -- jfmutil jodel [b][z]jlreq [b][z]jlreq
    jfmutil_jodel(p .. "jlreq-v", p .. "jlreq")
    -- for upTeX yoko
    -- jfmutil jodel u[b][z]jlreq u[b][z]jlreq
    jfmutil_jodel("u" .. p .. "jlreq", p .. "jlreq")
    -- for upTeX tate
    -- jfmutil jodel u[b][z]jlreq-v u[b][z]jlreq
    jfmutil_jodel("u" .. p .. "jlreq-v", p .. "jlreq")
  end
  return 0
end

function makejvf()
  jfmutil_jodel_jlreq()
end
