import asyncio, sys
sys.path.insert(0, '.')
from module1.services.ai_grader import ai_grade

async def main():
    try:
        res = await ai_grade(
            assignment_title='测试题',
            assignment_desc='请写一篇短文',
            max_score=100,
            is_late=False,
            late_score=60,
            teacher_file_path='',
            student_file_path='',
        )
        print('res=', res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
