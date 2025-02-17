if mode == "draft" then
  Make:htlatex()
else
  local domakeindex = false
  Make:add("xelatex", "-no-pdf", "-interaction=nonstopmode", Make.source)
  Make:add("xelatex", "-no-pdf", "-interaction=nonstopmode", Make.source)
  if domakeindex then
    Make:add("makeindex", Make.source)
    Make:add("xelatex", "-no-pdf", "-interaction=nonstopmode", Make.source)
  end
  Make:add("tex4ht -f/"..Make.source)
  Make:add("t4ht -f/"..Make.source)
end
