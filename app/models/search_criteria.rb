class SearchCriteria
  attr_accessor :search_text
  attr_reader   :section_ids
  attr_reader   :status
  attr_reader   :certification

  def initialize(attrs={})
    @certification = false
    attrs.each do |name, value|
      send("#{name}=", value)
    end
  end

  def section_ids=(value)
    @section_ids = value.delete_if { |item| item.nil? || item.size == 0}
  end

  def status=(value)
    @status = value.delete_if { |item| item.nil? || item.size == 0}
  end

  def search_certification=(value)
    @certification = ActiveRecord::Type::Boolean.new.type_cast_from_database(value)
  end

  def search_certification
    certification ? '1' : '0'
  end

  def present?
    !search_text.blank? || (section_ids && section_ids.count > 0) ||
        (status && status.count > 0) || certification
  end

  def to_s
    "search_text: #{search_text} status: #{status} certification: #{certification} search_certification: #{search_certification}"
  end
end