#!/usr/bin/env texlua
kpse.set_program_name("kpsewhich")

local lfs = require("lfs")

tfmfiledir = tfmfiledir or "./tfm"

local font_series_list = {
  {"minl","ml"},
  {"minr","mr"},
  {"minb","mb"},
  {"gothr","gr"},
  {"gothb","gb"},
  {"gotheb","ge"},
  {"mgothr","mgr"},
}

local function chekc_jfm(jlreq_tfm, deluxe_tfm)
  local jlreq_path = assert(kpse.find_file(jlreq_tfm, "tfm", true))
  local jlreq_file = assert(io.open(jlreq_path, "rb"))
  local jlreq_data = jlreq_file:read("*all")
  jlreq_file:close()

  local deluxe_file = assert(io.open(deluxe_tfm, "rb"))
  local deluxe_data = deluxe_file:read("*all")
  deluxe_file:close()

  return (jlreq_data == deluxe_data)
end

local function chekc_jfm_all(tfmdir)
  local error_count = 0
  for _,b in ipairs({ "", "b" }) do
    for _,z in ipairs({ "", "z" }) do
      for u = 1, 2 do
        for _,e in ipairs({ "nml", "exp", "ruby" }) do
          for _,s in pairs(font_series_list) do
            for _,n in ipairs({ "", "n" }) do
              for v = 1, 2 do -- in ipairs({ {"","-h"}, {"-v","-v"} })
                if not (e == "ruby" and n == "n") then
                  local ju = {"","u"}
                  local jv = {"","-v"}
                  local jlreq = ju[u] .. b .. z .. "jlreq" .. jv[v] .. ".tfm"
                  local du = {"","up"}
                  local dv = {"-h","-v"}
                  local deluxe = b .. z .. "jlreq--" .. du[u] .. e .. s[1] .. n .. dv[v] .. ".tfm"
                  if not chekc_jfm(jlreq, tfmdir .. "/" .. deluxe) then
                    error_count = error_count + 1
                    print("error: JFM difference between `" .. jlreq .. "' and `" .. deluxe .."'.")
                  end
                end
              end
            end
          end
        end
      end
    end
  end
  if error_count == 0 then
    print("OK")
  else
    print(string.format("%d JFM file(s) difference.", error_count))
  end
end

chekc_jfm_all(tfmfiledir)
