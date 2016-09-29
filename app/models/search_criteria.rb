class SearchCriteria
  attr_accessor :search_text
  attr_reader   :section_ids
  attr_reader   :status

  def initialize(attrs={})
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

  def present?
    !search_text.empty? || section_ids.count > 0 || status.count > 0
  end
end