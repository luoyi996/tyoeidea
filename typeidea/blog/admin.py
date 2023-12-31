from django.contrib import admin

# Register your models here.
from django.urls import reverse
from django.utils.html import format_html

from .adminforms import PostAdminForm
from .models import Post, Category, Tag
from typeidea.custom_site import custom_site


class PostInline(admin.TabularInline):  # StackedInline -- 样式不一样
    fields = ('title', 'desc')
    extra = 1  # 控制额外多几个
    model = Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [PostInline, ]
    list_display = ('name', 'status', 'is_nav', 'created_time')
    fields = ('name', 'status', 'is_nav')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


class CategoryOwnerFilter(admin.SimpleListFilter):
    """自定义过滤器只展示当前用户分类"""
    title = "分类过滤器"
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=category_id)
        else:
            return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    # 列表页面可展示字段
    list_display = [
        'title', 'category', 'status', 'created_time', 'operator'
    ]
    # 那些字段可以作为链接
    list_display_links = []
    # 通过那些字段过滤list_display列表页
    list_filter = [CategoryOwnerFilter]
    # 配置搜索字段
    search_fields = ['title', 'category__name']
    # 动作相关配置，是否展示在顶部
    actions_on_top = True
    # 动作相关配置，是否展示在底部
    actions_on_bottom = True

    # 保存、编辑、新建按钮是否在顶部展示
    save_on_top = True

    exclude = ('owner',)

    # 页面展示字段
    # fields = (
    #     ('category', 'title'),
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )
    fieldsets = (
        (
            "基础配置", {
                'description': "基础配置描述",
                'fields': (
                    ('title', 'category'),
                    'status',
                ),
            }
        ),
        (
            '内容', {
                'fields': (
                    'desc',
                    'content',
                ),
            }
        ),
        (
            '额外信息', {
                'classes': ('collapse',),
                'fields': ('tag',),
            }
        ),
    )

    # 自定义在list_display页面展示字段
    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id,))
        )

    # operator方法所展示的文本
    operator.short_description = "操作"

    # 自动设置作者名为request.user登录名
    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    class Media:
        css = {
            'all': ("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css",),
        }
        js = ("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js",)
