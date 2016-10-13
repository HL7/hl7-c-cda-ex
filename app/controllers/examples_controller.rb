class ExamplesController < ApplicationController
  before_action :set_example, only: [:show]

  # GET /examples
  # GET /examples.json
  def index
    if params[:search]
      @search = SearchCriteria.new(params[:search])
      logger.debug "Got search params: #{params[:search]}"
      @examples = Example.query(@search)
    else
      @search = SearchCriteria.new
      @examples = Example.all
    end
  end

  # GET /examples/1
  # GET /examples/1.json
  def show
    respond_to do |format|
      format.html
      format.xml do
        #response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = "attachment; filename=#{@example.name}.xml"
        render layout: false
      end
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_example
      @example = Example.find(params[:id])
    end
end
