local elu = {}

local function escape(s)
    s = string.gsub(s, "\\", "\\\\")
    s = string.gsub(s, "\n", "\\n")
    return s
end

local function eval(s, t)
    local _ENV = _ENV
    for k, v in pairs(t) do _ENV[k] = v end
    return assert(load(s, "eval", "t"))()
end

function elu.new(s)
    local obj = {}

    local list = {}
    local st = 1
    while st <= string.len(s) do
        local ed = string.find(s, "<%", st, true)
        if not ed then
            table.insert(list, { 0, string.sub(s, st, -1) })
            break
        end
        if st < ed then
            table.insert(list, { 0, string.sub(s, st, ed-1) })
        end
        st = ed + 2

        ed = string.find(s, "%>", st, true)
        if not ed then
            return nil
        end
        if st < ed then
            if string.sub(s, st, st) == "=" then
                table.insert(list, { 1, string.sub(s, st+1, ed-1) })
            else
                table.insert(list, { 2, string.sub(s, st, ed-1) })
            end
        end
        st = ed + 2
    end

    obj.list = list

    return obj
end

function elu.src(e)
    local s = ""
    for i, v in ipairs(e.list) do
        local k, t = v[1], v[2]
        if k == 0 then
            s = s .. "io.write(\"" .. escape(t) .. "\")\n"
        elseif k == 1 then
            s = s .. "io.write(tostring(" .. t .. "))\n"
        elseif k == 2 then
            s = s .. t .. "\n"
        end
    end
    return s
end

function elu.run(e, t)
    eval(elu.src(e), t)
end

function elu.result(e, t)
    local s = "local elu = \"\"\n"
    for i, v in ipairs(e.list) do
        local k, t = v[1], v[2]
        if k == 0 then
            s = s .. "elu = elu .. \"" .. escape(t) .. "\"\n"
        elseif k == 1 then
            s = s .. "elu = elu .. tostring(" .. t .. ")\n"
        elseif k == 2 then
            s = s .. t .. "\n"
        end
    end
    s = s .. "return elu"

    return eval(s, t)
end

return elu