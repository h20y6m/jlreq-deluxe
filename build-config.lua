
dvipdfexe  = dvipdfexe or "dvipdfmx"
dvipdfopts = dvipdfopts or ""

function dvipdf(name,dir)
  local dir = dir or "."
  if fileexists(dir .. "/" .. name .. ".dvi") then
    return run(dir, dvipdfexe .. " " .. dvipdfopts .. " " .. name .. ".dvi")
  end
  return 0
end

typeset = function(file,dir)
  dir = dir or "."
  local errorlevel = tex(file,dir)
  if errorlevel ~= 0 then
    return errorlevel
  end
  local name = jobname(file)
  errorlevel = biber(name,dir) + bibtex(name,dir)
  if errorlevel ~= 0 then
    return errorlevel
  end
  for i = 2,typesetruns do
    errorlevel =
      makeindex(name,dir,".glo",".gls",".glg",glossarystyle) +
      makeindex(name,dir,".idx",".ind",".ilg",indexstyle)    +
      tex(file,dir)
    if errorlevel ~= 0 then break end
  end
  if errorlevel ~= 0 then
    return errorlevel
  end
  errorlevel = dvipdf(name,dir)
  return errorlevel
end
