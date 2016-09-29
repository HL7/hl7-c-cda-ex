module ApplicationHelper
  def is_admin?
    false
  end

  def markdown
    @markdown ||= Redcarpet::Markdown.new(Redcarpet::Render::HTML, autolink: true, tables: true)
  end

  def maruku_string(content)
    Maruku.new(content).to_s
  end

  def syntax_highlight(content)
    @formatter ||= Rouge::Formatters::HTMLPygments.new(Rouge::Formatters::HTML.new)
    @lexer ||= Rouge::Lexers::XML.new
    @formatter.format(@lexer.lex(content))
  end
end
